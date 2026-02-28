import frappe

def execute():
if not frappe.db.exists("DocType", "Salesforce Settings"):
= frappe.get_doc({
pe": "DocType",
ame": "Salesforce Settings",
"Salesforce",
0,
gle": 1,
[
ame": "max_visits_per_day",
pe": "Int",
"Maximum Visits per Salesman per Day",
"20"
ame": "max_backdated_days",
pe": "Int",
"Maximum Backdated Posting Days",
"3"
sert(ignore_permissions=True)
t("Settings DocType created.")
else:
t("Settings DocType already exists.")

execute()
