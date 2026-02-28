import frappe

def create_reports():
    # 1. Create Report: Daily Activities Summary
    if not frappe.db.exists("Report", "Daily Activities Summary"):
        report = frappe.get_doc({
            "doctype": "Report",
            "report_name": "Daily Activities Summary",
            "ref_doctype": "Salesforce Activity",
            "report_type": "Report Builder",
            "is_standard": "Yes",
            "module": "Salesforce",
            "json": '{"columns":[["subject","Salesforce Activity","200px"],["activity_type","Salesforce Activity","150px"],["docstatus","Salesforce Activity","100px"],["sales_person","Salesforce Activity","150px"],["party","Salesforce Activity","150px"],["start_datetime","Salesforce Activity","150px"]],"filters":[["Salesforce Activity","start_datetime","Timespan","today",false]],"sort_by":"start_datetime","sort_order":"desc","add_totals_row":0}'
        })
        report.insert(ignore_permissions=True)
        print("Created Report: Daily Activities Summary")
    else:
        print("Report 'Daily Activities Summary' already exists.")

    # 2. Create Expected vs Completed logic via standard Report Builder filtering
    if not frappe.db.exists("Report", "Planned Calls Status"):
        report = frappe.get_doc({
            "doctype": "Report",
            "report_name": "Planned Calls Status",
            "ref_doctype": "Salesforce Activity",
            "report_type": "Report Builder",
            "is_standard": "Yes",
            "module": "Salesforce",
            "json": '{"columns":[["subject","Salesforce Activity","200px"],["party","Salesforce Activity","150px"],["docstatus","Salesforce Activity","100px"],["start_datetime","Salesforce Activity","150px"]],"filters":[["Salesforce Activity","activity_type","=","Planned Call",false]],"sort_by":"start_datetime","sort_order":"desc"}'
        })
        report.insert(ignore_permissions=True)
        print("Created Report: Planned Calls Status")
    else:
        print("Report 'Planned Calls Status' already exists.")

    # 3. Create Number Card: Total Planned Calls Today
    if not frappe.db.exists("Number Card", "My Planned Calls Today"):
        card = frappe.get_doc({
            "doctype": "Number Card",
            "document_type": "Salesforce Activity",
            "name": "My Planned Calls Today",
            "label": "My Planned Calls Today",
            "function": "Count",
            "is_standard": 1,
            "module": "Salesforce",
            "filters_json": '[["Salesforce Activity","activity_type","=","Planned Call",false],["Salesforce Activity","docstatus","=","0",false]]'
        })
        card.insert(ignore_permissions=True)
        print("Created Number Card: My Planned Calls Today")
    else:
        print("Number Card 'My Planned Calls Today' already exists.")

    # 4. Create Number Card: Completed Activities Today
    if not frappe.db.exists("Number Card", "My Completed Activities Today"):
        card2 = frappe.get_doc({
            "doctype": "Number Card",
            "document_type": "Salesforce Activity",
            "name": "My Completed Activities Today",
            "label": "My Completed Activities Today",
            "function": "Count",
            "is_standard": 1,
            "module": "Salesforce",
            "filters_json": '[["Salesforce Activity","docstatus","=","1",false]]'
        })
        card2.insert(ignore_permissions=True)
        print("Created Number Card: My Completed Activities Today")
    else:
        print("Number Card 'My Completed Activities Today' already exists.")

    frappe.db.commit()
