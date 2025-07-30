// Copyright (c) 2025, Golive Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salla Sync Job', {
	update_bulk_warehouse: function (frm) {
		if (!(frm.doc.warehouse || frm.doc.merchant)) return;

		frappe.call({
			method: "salla_common.utils.update_product_balance_warehouse",
			args: {
				merchant: frm.doc.merchant, 
			}
		});
	}
});
