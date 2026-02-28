# Copyright (c) 2026, Salesforce and contributors
# For license information, please see license.txt

import frappe
import json

def execute(filters=None):
	columns, data = [], []
	
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "document_id",
			"label": "Document ID",
			"fieldtype": "Link",
			"options": "Salesforce Activity",
			"width": 150
		},
		{
			"fieldname": "date_time",
			"label": "Date/Time",
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "activity_type",
			"label": "Activity Type",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "sales_person",
			"label": "Sales Person",
			"fieldtype": "Link",
			"options": "Sales Person",
			"width": 120
		},
		{
			"fieldname": "party_type",
			"label": "Party Type",
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Dynamic Link",
			"options": "party_type",
			"width": 150
		},
		{
			"fieldname": "customer_name",
			"label": "Customer Name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "lat_long",
			"label": "Lat/Long",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "image_displayed",
			"label": "Image Displayed",
			"fieldtype": "Data",
			"width": 600
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql("""
		SELECT
			a.name AS document_id,
			a.start_datetime AS date_time,
			a.activity_type AS activity_type,
			a.sales_person AS sales_person,
			a.party_type AS party_type,
			a.party AS customer,
			a.party_name AS customer_name,
			a.location AS location,
			(SELECT image FROM `tabSalesforce Activity Image` WHERE parent = a.name ORDER BY idx LIMIT 1) AS image_displayed
		FROM
			`tabSalesforce Activity` a
		WHERE 
			1=1 {conditions}
		ORDER BY 
			a.start_datetime DESC
	""".format(conditions=conditions), filters, as_dict=1)
	
	for row in data:
		lat_long = ""
		if row.get("location"):
			try:
				loc = json.loads(row.location)
				if loc.get("features") and len(loc["features"]) > 0:
					coords = loc["features"][0].get("geometry", {}).get("coordinates", [])
					if len(coords) >= 2:
						lat_long = f"{coords[1]}, {coords[0]}" # Lat, Long
			except Exception:
				lat_long = "Parsing Error"
		row["lat_long"] = lat_long

	return data

def get_conditions(filters):
	conditions = ""
	if filters.get("start_datetime"):
		filters["start_date"] = filters.get("start_datetime")[0]
		filters["end_date"] = filters.get("start_datetime")[1]
		conditions += " AND DATE(a.start_datetime) BETWEEN %(start_date)s AND %(end_date)s"
	
	if filters.get("sales_person"):
		conditions += " AND a.sales_person = %(sales_person)s"
		
	if filters.get("docstatus") not in (None, ""):
		conditions += " AND a.docstatus = %(docstatus)s"
		
	return conditions
