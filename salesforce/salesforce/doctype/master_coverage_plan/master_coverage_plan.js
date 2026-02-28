// Copyright (c) 2026, Me and contributors
// For license information, please see license.txt

frappe.ui.form.on("Master Coverage Plan", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Generate Planned Calls'), function () {
                frappe.call({
                    method: 'salesforce.salesforce.doctype.master_coverage_plan.master_coverage_plan.generate_planned_calls_on_demand',
                    args: {
                        mcp_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Generating planned calls...'),
                    callback: function (r) {
                        if (!r.exc) {
                            let count = r.message || 0;
                            frappe.msgprint({
                                title: __('Success'),
                                indicator: 'green',
                                message: __('Successfully generated {0} Planned Calls for today.', [count])
                            });
                        }
                    }
                });
            }, __('Actions'));
        }
    }
});
