// Copyright (c) 2026, Salesforce and contributors
// For license information, please see license.txt

frappe.query_reports["Salesforce Activity Detail"] = {
    "filters": [
        {
            "fieldname": "start_datetime",
            "label": __("Start Date"),
            "fieldtype": "DateRange",
            "width": "80"
        },
        {
            "fieldname": "sales_person",
            "label": __("Sales Person"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": "80"
        },
        {
            "fieldname": "docstatus",
            "label": __("Document Status"),
            "fieldtype": "Select",
            "options": [
                { "value": "", "label": __("All") },
                { "value": 0, "label": __("Draft") },
                { "value": 1, "label": __("Submitted") },
                { "value": 2, "label": __("Cancelled") }
            ],
            "default": "",
            "width": "80"
        }
    ],
    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname === "image_displayed" && data && data.image_displayed) {
            value = `<img src="${data.image_displayed}" style="max-height: 600px; max-width: 600px;">`;
        }
        return value;
    },
    "get_datatable_options": function (options) {
        options.rowHeight = 600;
        return options;
    },
    "onload": function (report) {
        frappe.dom.set_style(`
            .frappe-datatable .dt-row { height: 600px !important; }
            .frappe-datatable .dt-cell { height: 600px !important; align-items: center; }
        `);
    }
};
