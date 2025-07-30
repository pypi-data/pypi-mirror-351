app_name = "salla_common"
app_title = "Salla Common"
app_publisher = "Golive Solutions"
app_description = "App For Salla Comman Features"
app_email = "info@golive-solutions.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/salla_common/css/salla_common.css"
# app_include_js = "/assets/salla_common/js/salla_common.js"

# include js, css files in header of web template
# web_include_css = "/assets/salla_common/css/salla_common.css"
# web_include_js = "/assets/salla_common/js/salla_common.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "salla_common/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"Item": "public/js/item.js"}
doctype_js = {
    "Salla Order": "public/js/salla_order.js",
    "Salla Order Fulfillment": "public/js/salla_order_fulfillment.js",
    "Salla Shipment Method Mapping": "public/js/salla_shipment_method_mapping.js",
    "Item": "public/js/item.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#     "Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#     "methods": "salla_common.utils.jinja_methods",
#     "filters": "salla_common.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "salla_common.install.before_install"
# after_install = "salla_common.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "salla_common.uninstall.before_uninstall"
# after_uninstall = "salla_common.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "salla_common.utils.before_app_install"
# after_app_install = "salla_common.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "salla_common.utils.before_app_uninstall"
# after_app_uninstall = "salla_common.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "salla_common.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#     "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#     "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#     "ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Salla Order": {
        "validate": "salla_common.event.salla_order.validate",
        "before_save": "salla_common.event.salla_order.before_save",
        "before_insert": "salla_common.event.salla_order.before_insert",
        "before_update_after_submit": "salla_common.event.salla_order.before_update_after_submit",
        "on_cancel": "salla_common.event.salla_order.on_cancel",
        "before_submit": "salla_common.event.salla_order.before_submit"
    },
    "Item": {
        "before_save": "salla_common.event.item.before_save",
        "on_update": "salla_common.event.item.on_update",
    },
    "Item Price": {
        "before_save": "salla_common.event.item_price.before_save",
    }, 
}
# doc_events = {
   
# }
# Scheduled Tasks
# ---------------

# scheduler_events = {
#     "all": [
#         "salla_common.tasks.all"
#     ],
#     "daily": [
#         "salla_common.tasks.daily"
#     ],
#     "hourly": [
#         "salla_common.tasks.hourly"
#     ],
#     "weekly": [
#         "salla_common.tasks.weekly"
#     ],
#     "monthly": [
#         "salla_common.tasks.monthly"
#     ],
# }

# Testing
# -------

# before_tests = "salla_common.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "salla_common.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#     "Task": "salla_common.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["salla_common.utils.before_request"]
# after_request = ["salla_common.utils.after_request"]

# Job Events
# ----------
# before_job = ["salla_common.utils.before_job"]
# after_job = ["salla_common.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#     {
#         "doctype": "{doctype_1}",
#         "filter_by": "{filter_by}",
#         "redact_fields": ["{field_1}", "{field_2}"],
#         "partial": 1,
#     },
#     {
#         "doctype": "{doctype_2}",
#         "filter_by": "{filter_by}",
#         "partial": 1,
#     },
#     {
#         "doctype": "{doctype_3}",
#         "strict": False,
#     },
#     {
#         "doctype": "{doctype_4}"
#     }
# ]

# Authentication and authorization
# --------------------------------
export_python_type_annotations = True

# auth_hooks = [
#     "salla_common.auth.validate"
# ]
fixtures = [
    {
        "dt": "Custom Field",
        "filters": {
            "name": [
                "in",
                [
                    "Item-custom_salla",
                    "Item-custom_salla_item",
                    "Item-custom_is_bundle",
                    "Item-custom_concatenated_barcode",
                    "Item-custom_is_salla_item",
                    "Item-custom_product_image",
                    "Item-custom_product_type",
                    "Item-custom_send_item_to_salla",
                    "Item-custom_salla_variant_id",
                    "Item-custom_update_pending_online_quantity",
                    "Item Barcode-custom_is_salla_barcode",
                ],
            ]
        },
    }
]