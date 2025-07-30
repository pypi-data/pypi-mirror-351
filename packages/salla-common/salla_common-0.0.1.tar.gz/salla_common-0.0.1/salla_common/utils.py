import datetime
import requests
import frappe
from frappe.utils.data import getdate, now_datetime, today
from erpnext.stock.dashboard.item_dashboard import (
    get_data,
)

salla_base_url = "https://api.salla.dev/admin/v2"
update_bulk_url = "products/quantities/bulkSkus"

def create_or_update_salla_item(doc, merchant_name):
    """Main function to sync an item with Salla."""
    try:
        # Skip if item should not be sent to Salla
        if not doc["custom_send_item_to_salla"]:
            return {"success": True, "message": "Item not configured to send to Salla"}

        merchant = frappe.get_doc("Salla Settings", merchant_name)
        barcode = get_salla_barcode(doc["name"])

        if not barcode:
            return {
                "success": False,
                "error": f"No Salla barcode found for item {doc['name']}",
            }

        headers = get_salla_auth_headers(merchant)
        base_url = "https://api.salla.dev/admin/v2"

        result = None

        if doc["variant_of"]:
            result = handle_variant_item(doc, barcode, headers, base_url)
        else:
            result = handle_standard_item(doc, barcode, headers, base_url)

        return result

    except Exception as e:
        frappe.log_error(f"Error syncing item {doc['name']} with Salla", str(e))
        return {"success": False, "error": str(e)}


# Update handle_standard_item to return a response
def handle_standard_item(doc, barcode, headers, base_url):
    """Handle syncing of standard (non-variant) items."""
    try:
        item_data = prepare_item_data(doc, barcode)
        response = get_product_details(headers, base_url, barcode)

        if response.status_code == 200:
            update_response = update_item_by_barcode(
                headers, base_url, barcode, item_data
            )
            if update_response.status_code == 201:
                return {
                    "success": True,
                    "message": "Item updated successfully",
                    "item_info": doc["name"],
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to update item. Status: {update_response.status_code}, Reason: {update_response.reason}",
                }
        else:
            # Add image to item data
            item_data["images"] = [{"original": doc.custom_product_image}]
            add_response = add_new_salla_item(headers, base_url, item_data)

            if add_response.status_code == 201:
                return {
                    "success": True,
                    "message": "New item created successfully",
                    "item_info": doc["name"],
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create new item. Status: {add_response.status_code}, Reason: {add_response.reason}",
                }

    except Exception as e:
        return {"success": False, "error": str(e)}


# Update handle_variant_item to return a response
def handle_variant_item(doc, barcode, headers, base_url):
    """Handle syncing of variant items."""
    try:
        # Get parent item details
        parent_doc = frappe.get_doc("Item", doc["variant_of"])
        parent_barcode = get_salla_barcode(parent_doc["name"])

        if not parent_barcode:
            return {
                "success": False,
                "error": f"No Salla barcode found for parent item {parent_doc['name']}",
            }

        # Get parent product details from Salla
        parent_product_response = get_product_details(headers, base_url, parent_barcode)

        if parent_product_response.status_code != 200:
            return {
                "success": False,
                "error": f"Parent product not found in Salla. Status: {parent_product_response.status_code}",
            }

        parent_product_data = parent_product_response.json()
        parent_product_id = parent_product_data.get("data", {}).get("id")
        options = parent_product_data.get("data", {}).get("options", [])

        # Process attributes and option values
        values_id = process_attributes(
            doc, options, headers, base_url, parent_product_id
        )

        # Update or set variant ID
        if doc["custom_salla_variant_id"]:
            result = update_existing_variant(doc, barcode, headers, base_url)
            return {
                "success": result.get("status", False),
                "message": "Variant updated successfully",
            }
        else:
            result = find_or_create_variant(
                doc, parent_barcode, headers, base_url, values_id
            )
            return {
                "success": True,
                "message": "Variant processed successfully",
            }

    except Exception as e:
        return {"success": False, "error": str(e)}
    
def get_salla_barcode(doc_name):
    """Get the Salla barcode for an item."""
    return frappe.get_doc(
        "Item Barcode", {"parent": doc_name, "custom_is_salla_barcode": 1}
    )

def get_salla_auth_headers(merchant_settings):
    headers = {
        "Authorization": f"Bearer {merchant_settings.access_token}",
        "Content-Type": "application/json",
    }
    return headers

def prepare_item_data(doc, barcode):
    """Prepare basic item data for Salla API."""
    return {
        "name": doc["item_name"],
        "price": doc["standard_rate"],
        "sku": barcode.barcode,
        "product_type": doc["custom_product_type"],
        "description": f"<strong>{doc['description']}</strong>",
    }

def get_product_details(headers, salla_base_url, barcode):
    check_url = f"{salla_base_url}/products/sku/{barcode.barcode}"
    return requests.get(check_url, headers=headers)


def update_item_by_barcode(headers, salla_base_url, barcode, item_data):
    update_url = f"{salla_base_url}/products/sku/{barcode.barcode}"
    return requests.put(update_url, json=item_data, headers=headers)

def add_new_salla_item(headers, salla_base_url, item_data):
    add_url = f"{salla_base_url}/products"
    return requests.post(add_url, json=item_data, headers=headers)

def process_attributes(doc, options, headers, base_url, parent_product_id):
    """Process item attributes for Salla sync."""
    values_id = []
    new_option_count = 0

    for attribute in doc["attributes"]:
        print(type(attribute))
        option = next(
            (opt for opt in options if opt.get("name") == attribute.attribute),
            None,
        )

        if option:
            # Option exists, find or create value
            process_option_value(option, attribute, values_id, headers, base_url)
        elif new_option_count < 2:
            # Create new option (max 2)
            create_new_option(attribute, parent_product_id, headers, base_url)
            new_option_count += 1

    return values_id


def process_option_value(option, attribute, values_id, headers, base_url):
    """Process option values for a given attribute."""
    value = next(
        (
            val
            for val in option.get("values")
            if val.get("name") == attribute.attribute_value
        ),
        None,
    )

    if value:
        values_id.append(value.get("id"))
    else:
        # Create missing value
        value_data = {"name": attribute.attribute_value}
        response = create_product_option_value(
            headers, base_url, option.get("id"), value_data
        )

        if response.status_code == 201:
            frappe.msgprint(f"Value {attribute.attribute_value} added successfully")
            values_data = response.json().get("data", {})
            for val_data in values_data:
                values_id.append(val_data.get("id"))
        else:
            frappe.throw(f"Failed to add value {attribute.attribute_value}.")


def create_new_option(attribute, parent_product_id, headers, base_url):
    """Create a new option for a parent product."""
    option_data = {
        "name": attribute.attribute,
        "type": "radio",
        "values": [{"name": attribute.attribute_value}],
    }

    response = create_product_option(headers, base_url, parent_product_id, option_data)

    if response.status_code == 201:
        frappe.msgprint(f"Option {attribute.attribute} created successfully")
    else:
        frappe.msgprint("Failed to create option.")


def create_product_option(headers, salla_base_url, product_id, option_data):
    create_product_option_url = f"{salla_base_url}/products/{product_id}/options"
    return requests.post(create_product_option_url, json=option_data, headers=headers)


def create_product_option_value(headers, salla_base_url, option_id, option_data):
    create_product_option_value_url = f"{salla_base_url}/products/options/{option_id}"
    return requests.post(
        create_product_option_value_url, json=option_data, headers=headers
    )

def update_existing_variant(doc, barcode, headers, base_url):
    """Update an existing variant in Salla."""
    variant_data = {"sku": barcode.barcode, "weight": doc["weight_per_unit"]}

    update_response = update_product_variant(
        headers, base_url, doc["custom_salla_variant_id"], variant_data
    )

    if isinstance(update_response, dict) and update_response.get("status"):
        frappe.msgprint("Variant updated successfully.")
    else:
        frappe.throw("Failed to update item variant.")

    return update_response


def find_or_create_variant(doc, parent_barcode, headers, base_url, values_id):
    """Find existing variant or create a new one based on option values."""
    parent_product_response = get_product_details(headers, base_url, parent_barcode)
    parent_product_data = parent_product_response.json()

    # Check if variant already exists with the same option values
    for sku in parent_product_data.get("data", {}).get("skus", []):
        if set(sku.get("related_option_values", [])) == set(values_id):
            save_variant_id(doc, sku.get("id"))
            {
                "success": True,
                "message": f"Found and linked existing variant for {doc['name']}",
            }


def save_variant_id(doc, variant_id):
    """Save the variant ID to the item document."""
    frappe.db.set_value("Item", doc["name"], "custom_salla_variant_id", variant_id)
    frappe.db.commit()

def update_product_variant(headers, salla_base_url, variant, variant_data):
    update_product_variant_url = f"{salla_base_url}/products/variants/{variant}"
    response = requests.put(
        update_product_variant_url, json=variant_data, headers=headers
    )
    return response.json()

def update_salla_price(item_price):
    if "selling" in item_price and "valid_from" in item_price:
        today = getdate()
        if item_price["selling"] and getdate(item_price["valid_from"]) == today:
            item = frappe.get_doc("Item", item_price["item_code"])
            print(f"salla item: {item.custom_is_salla_item}")
            print(item)
            print(f"price_list: {item_price['price_list']}")
            if item.custom_is_salla_item:
                merchant_salla_setting_list = frappe.get_list(
                    "Salla Defaults", filters={"price_list": item_price["price_list"]}
                )

                print(f"merchant_salla_setting_list: {merchant_salla_setting_list}")
                for salla_setting in merchant_salla_setting_list:
                    # handle updating price for variant items
                    salla_setting_doc = frappe.get_doc("Salla Settings", salla_setting.name)
                    if salla_setting_doc.update_product_price:
                        if item.variant_of:
                            response = update_variant_price(
                                item, item_price["price_list_rate"], salla_setting.name
                            )
                            return response
                        else:
                            response = update_price_using_barcode(
                                item_price["item_code"],
                                item_price["price_list_rate"],
                                salla_setting.name,
                            )
                            return response
                
def update_variant_price(item_variant, price, merchant_name):
    merchant_settings = frappe.get_doc("Salla Settings", merchant_name)
    headers = get_salla_auth_headers(merchant_settings)
    data = {"price": price}

    response = update_product_variant(
        headers, salla_base_url, item_variant.custom_salla_variant_id, data
    )
    return response

@frappe.whitelist()
def update_price_using_barcode(item, price, merchant_name):
    doc = frappe.get_doc("Item", item)
    merchant = frappe.get_doc("Salla Settings", merchant_name)
    barcode = frappe.get_doc(
        "Item Barcode", {"parent": doc.name, "custom_is_salla_barcode": 1}
    )
    headers = {
        "Authorization": f"Bearer {merchant.access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {"price": price}

    print(f"data : {data}")
    response = requests.post(
        f"{salla_base_url}/products/sku/{barcode.barcode}/price",
        headers=headers,
        data=data,
    )
    print(
        f"API response status: {response.status_code}, response body: {response.text}"
    )

    return response


@frappe.whitelist()
def update_product_balance_warehouse(merchant_name=None, item=None):
    payload = format_doc_for_reception(merchant_name, item)
    if is_app_installed("salla_connector"):
        from salla_connector.salla_utils import update_product_balance_warehouse
        update_product_balance_warehouse(payload)
    elif is_app_installed("salla_client"):
        from salla_client.salla_utils import update_product_balance_warehouse
        update_product_balance_warehouse(payload)

@frappe.whitelist()
def update_variant_qty(item_variant, merchant_name, salla_item_info_name):
    payload = format_variant_data(item_variant, merchant_name, salla_item_info_name)
    if is_app_installed("salla_connector"):
        from salla_connector.salla_utils import update_variant_qty
        update_variant_qty(payload)
    elif is_app_installed("salla_client"):
        from salla_client.salla_utils import update_variant_qty
        update_variant_qty(payload)



def format_variant_data(item_variant, merchant_name, salla_item_info_name):
    custom_salla_variant_id = frappe.get_value("Item", item_variant, "custom_salla_variant_id")

    data = []
    qty = 0
    if not frappe.db.exists(
        "Salla Sync Job", merchant_name
    ):
        frappe.throw("You Have To Put Warehouse In Salla Sync Job")

    salla_job_setting = frappe.get_doc(
        "Salla Sync Job", merchant_name
    )

    if salla_job_setting.warehouse:
        report_doc = frappe.get_doc("Report", "Stock Projected Qty")
        columns, data = report_doc.get_data(
            filters={
            "warehouse": salla_job_setting.warehouse,
            "item_code": item_variant
        }, as_dict= 1)
        
        # print(warehouse_balance)
    salla_item_info = frappe.get_doc("Salla Item Info", salla_item_info_name)
    if len(data):
        qty = data[0]["actual_qty"] - salla_item_info.pending_online_quantity - data[0]["reserved_qty"] - data[0]["reserved_qty_for_pos"]
    return {
        "merchant_name": merchant_name,
        "custom_salla_variant_id": custom_salla_variant_id,
        "qty": qty
    }

def format_doc_for_reception(merchant_name=None, item=None):
    if not merchant_name and not item:
        frappe.throw("Please provide at least a merchant name or an item.")

    payload = {"merchants": []}
    data = []

    merchant_filters = {"name": merchant_name} if merchant_name else {}
    merchant_list = frappe.get_all(
        "Salla Merchant", filters=merchant_filters, fields=["name", "merchant_name"]
    )

    for merchant in merchant_list:
        merchant_data = {"merchant": merchant.name, "items": []}

        salla_job_setting = frappe.get_doc("Salla Sync Job", merchant.name)
        if not salla_job_setting:
            continue

        item_filters = {"merchant": merchant.name}
        item_filters.update(
            {"last_update": ("<", today())} if not item else {"parent": item}
        )

        merchant_item_info_list = frappe.get_all(
            "Salla Item Info",
            filters=item_filters,
            fields=[
                "name",
                "pending_online_quantity",
                "parent",
                "is_unlimited_qty",
            ],
            limit_page_length=salla_job_setting.product_balance_products_limit_per_request,
        )

        for info in merchant_item_info_list:
            if salla_job_setting.warehouse:
                report_doc = frappe.get_doc("Report", "Stock Projected Qty")
                columns, data = report_doc.get_data(
                    filters={
                    "warehouse": salla_job_setting.warehouse,
                    "item_code": info.parent
                }, as_dict= 1)

            salla_product_sku = frappe.get_value(
                "Item Barcode",
                filters={
                    "parent": info.parent,
                    "custom_is_salla_barcode": 1,
                },
                fieldname="barcode",
            )

            if not salla_product_sku:
                continue
            if len(data):
                quantity = data[0]["qty"] - info.pending_online_quantity - data[0]["reserved_qty"] - data[0]["reserved_qty_for_pos"]
            item_doc = frappe.get_doc("Item", info.parent)
            if item_doc.variant_of:
                variant_data = format_variant_data(item_doc,merchant.name,info.name)
                merchant_data["items"].append(variant_data)
            else:
                merchant_data["items"].append({
                    "sku": salla_product_sku,
                    "quantity": quantity,
                    "unlimited_quantity": bool(info.is_unlimited_qty),
                    "info_name": info.name,
                })

        payload["merchants"].append(merchant_data)

    return payload

def get_salla_defaults(doc):
    if frappe.db.exists("Salla Defaults", doc.merchant):
        return frappe.get_doc("Salla Defaults", doc.merchant)
    else:
        frappe.msgprint(f"Please Set Salla Deafults For Merchant {doc.merchant}")
        return
    
def get_pos_profile(doc,salla_default) :   
    if not salla_default.pos_profile :
        frappe.throw(f"Please Set POS Profile For Merchant {doc.merchant} in Salla Defaults")
        return
    else :
        PosProfileDoc = frappe.get_doc("POS Profile", salla_default.pos_profile)
        if salla_default.taxe_included_in_basic_rate:
            if not PosProfileDoc.taxes_and_charges:
                frappe.throw(f"Please Set Taxes and Charges For Merchant {doc.merchant} in Salla Defaults")
                return
    return  PosProfileDoc 

def is_app_installed(app_name):
    """Check if an app is installed."""
    installe_app_list = frappe.get_installed_apps()
    return app_name in installe_app_list