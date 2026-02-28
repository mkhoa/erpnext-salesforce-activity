import frappe

def create_workspace():
    if not frappe.db.exists("Workspace", "Salesforce"):
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Salesforce",
            "module": "Salesforce",
            "is_standard": 1,
            "for_user": "",
            "public": 1,
            "seq_no": 1,
            "icon": "user",
            "content": """[
                {"id":"header-reports","type":"header","data":{"text":"Salesman Dashboard","level":2,"col":12}},
                {"id":"card-planned","type":"number_card","data":{"number_card_name":"My Planned Calls Today","col":3}},
                {"id":"card-completed","type":"number_card","data":{"number_card_name":"My Completed Activities Today","col":3}},
                
                {"id":"header-actions","type":"header","data":{"text":"Activity Tracking","level":2,"col":12}},
                {"id":"shortcut-activities","type":"shortcut","data":{"shortcut_name":"My Activities","col":4}},
                {"id":"shortcut-planned","type":"shortcut","data":{"shortcut_name":"My Planned Calls","col":4}},
                {"id":"shortcut-mcps","type":"shortcut","data":{"shortcut_name":"My Coverage Plans","col":4}},
                
                {"id":"header-reports-links","type":"header","data":{"text":"Reports & Insights","level":2,"col":12}},
                {"id":"link-daily","type":"card","data":{"card_name":"Salesforce Reports","col":4}}
            ]""",
            "shortcuts": [
                {
                    "type": "DocType",
                    "link_to": "Salesforce Activity",
                    "label": "My Activities",
                    "format": "List"
                },
                {
                    "type": "DocType",
                    "link_to": "Salesforce Activity",
                    "label": "My Planned Calls",
                    "format": "List",
                    "stats_filter": '[["Salesforce Activity","activity_type","=","Planned Call",false],["Salesforce Activity","docstatus","=","0",false]]'
                },
                {
                    "type": "DocType",
                    "link_to": "Master Coverage Plan",
                    "label": "My Coverage Plans",
                    "format": "List"
                }
            ],
            "links": [
                {
                    "type": "Card Break",
                    "label": "Salesforce Reports"
                },
                {
                    "type": "Report",
                    "link_to": "Daily Activities Summary",
                    "label": "Daily Activities Summary",
                    "is_query_report": 1
                },
                {
                    "type": "Report",
                    "link_to": "Planned Calls Status",
                    "label": "Planned Calls Status",
                    "is_query_report": 1
                }
            ]
        })
        workspace.insert(ignore_permissions=True)
        print("Created typical Salesforce Workspace.")
    else:
        # Update existing
        workspace = frappe.get_doc("Workspace", "Salesforce")
        workspace.content = """[
            {"id":"header-reports","type":"header","data":{"text":"Salesman Dashboard","level":2,"col":12}},
            {"id":"card-planned","type":"number_card","data":{"number_card_name":"My Planned Calls Today","col":3}},
            {"id":"card-completed","type":"number_card","data":{"number_card_name":"My Completed Activities Today","col":3}},
            
            {"id":"header-actions","type":"header","data":{"text":"Activity Tracking","level":2,"col":12}},
            {"id":"shortcut-activities","type":"shortcut","data":{"shortcut_name":"My Activities","col":4}},
            {"id":"shortcut-planned","type":"shortcut","data":{"shortcut_name":"My Planned Calls","col":4}},
            {"id":"shortcut-mcps","type":"shortcut","data":{"shortcut_name":"My Coverage Plans","col":4}},
            
            {"id":"header-reports-links","type":"header","data":{"text":"Reports & Insights","level":2,"col":12}},
            {"id":"link-daily","type":"card","data":{"card_name":"Salesforce Reports","col":4}}
        ]"""
        
        # Add links if missing
        existing_links = [l.link_to for l in workspace.links]
        if "Daily Activities Summary" not in existing_links:
            workspace.append("links", {
                "type": "Card Break",
                "label": "Salesforce Reports"
            })
            workspace.append("links", {
                "type": "Report",
                "link_to": "Daily Activities Summary",
                "label": "Daily Activities Summary",
                "is_query_report": 1
            })
            workspace.append("links", {
                "type": "Report",
                "link_to": "Planned Calls Status",
                "label": "Planned Calls Status",
                "is_query_report": 1
            })
            
        workspace.save(ignore_permissions=True)
        print("Updated Salesforce Workspace with Reports and Dashboard metrics.")
        
    frappe.db.commit()

create_workspace()
