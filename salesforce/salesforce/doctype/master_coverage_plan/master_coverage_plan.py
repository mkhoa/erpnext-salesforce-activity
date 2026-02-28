# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.utils import today, getdate
import calendar
from frappe.model.document import Document


class MasterCoveragePlan(Document):
	pass


@frappe.whitelist()
def generate_planned_calls_on_demand(mcp_name):
	mcp_doc = frappe.get_doc("Master Coverage Plan", mcp_name)
	
	current_date = getdate(today())
	current_weekday = calendar.day_name[current_date.weekday()]
	week_of_month = (current_date.day - 1) // 7 + 1
	month = current_date.month
	month_of_quarter = (month - 1) % 3 + 1
	
	count = _process_mcp(mcp_doc, current_date, current_weekday, week_of_month, month_of_quarter)
	return count

@frappe.whitelist()
def generate_planned_calls():
	current_date = getdate(today())
	current_weekday = calendar.day_name[current_date.weekday()]
	week_of_month = (current_date.day - 1) // 7 + 1
	month = current_date.month
	month_of_quarter = (month - 1) % 3 + 1
	
	mcps = frappe.get_all("Master Coverage Plan", fields=["name", "sales_person"])
	
	for mcp in mcps:
		mcp_doc = frappe.get_doc("Master Coverage Plan", mcp.name)
		_process_mcp(mcp_doc, current_date, current_weekday, week_of_month, month_of_quarter)


DAILY_VISIT_CAP = 20


def _get_daily_count(sales_person, target_date, daily_counts):
	"""Return the number of planned calls already scheduled for sales_person on target_date.
	Uses an in-memory cache `daily_counts` during a single generation run.
	"""
	key = (sales_person, str(target_date))
	if key not in daily_counts:
		# Count existing Draft + Submitted planned calls in DB for that day
		count = frappe.db.count("Salesforce Activity", {
			"sales_person": sales_person,
			"activity_type": "Planned Call",
			"start_datetime": ["like", f"{target_date}%"],
			"docstatus": ["in", [0, 1]]
		})
		daily_counts[key] = count
	return daily_counts[key]


def _find_next_available_date(row, sales_person, start_date, daily_counts, max_days_ahead=60):
	"""Find the next calendar date (within max_days_ahead) that:
	1. Matches one of the customer's preferred weekdays.
	2. The salesman has fewer than DAILY_VISIT_CAP planned calls.
	Returns a date object or None if no slot is found within the window.
	"""
	from datetime import timedelta
	
	# Build a set of preferred calendar.day_name values from the checkboxes
	preferred_days = {
		day for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
		if getattr(row, day.lower(), 0) == 1
	}
	
	candidate = start_date
	for _ in range(max_days_ahead):
		candidate = candidate + timedelta(days=1)
		weekday_name = calendar.day_name[candidate.weekday()]
		
		if weekday_name not in preferred_days:
			continue
		
		if _get_daily_count(sales_person, candidate, daily_counts) < DAILY_VISIT_CAP:
			return candidate
	
	return None  # No slot found within the window


def _process_mcp(mcp_doc, current_date, current_weekday, week_of_month, month_of_quarter):
	generated_count = 0
	# Per-run in-memory cache: (sales_person, date_str) -> count
	daily_counts = {}
	
	for row in mcp_doc.customers:
		# Check if the checkbox for today's weekday is checked (1)
		is_preferred_day = getattr(row, current_weekday.lower(), 0) == 1
		
		if row.visit_frequency != "D1" and not is_preferred_day:
			continue
		
		should_visit = False
		freq = row.visit_frequency
		
		if freq == "D1":
			should_visit = True
		elif freq == "M1" and week_of_month == 1:
			should_visit = True
		elif freq == "M2" and week_of_month in [1, 3]:
			should_visit = True
		elif freq == "M4" and week_of_month <= 4:
			should_visit = True
		elif freq == "Q1" and month_of_quarter == 1 and week_of_month == 1:
			should_visit = True
		elif freq == "Q2" and month_of_quarter in [1, 2] and week_of_month == 1:
			should_visit = True
				
		if should_visit:
			# Skip if a planned call already exists for this customer & salesperson on any day
			existing = frappe.db.exists("Salesforce Activity", {
				"sales_person": mcp_doc.sales_person,
				"party_type": "Customer",
				"party": row.customer,
				"activity_type": "Planned Call",
				"start_datetime": ["like", f"{current_date}%"],
				"docstatus": ["in", [0, 1]]
			})
			if existing:
				continue
			
			# Determine the target date, respecting the daily cap
			target_date = current_date
			current_count = _get_daily_count(mcp_doc.sales_person, target_date, daily_counts)
			
			if current_count >= DAILY_VISIT_CAP:
				# Salesman is fully booked for today — find next available day
				target_date = _find_next_available_date(
					row, mcp_doc.sales_person, current_date, daily_counts
				)
			
			if target_date is None:
				# No slot available within 60 days — skip and log
				frappe.log_error(
					f"No available slot for {row.customer} (Sales Person: {mcp_doc.sales_person}) within 60 days.",
					"Planned Call Scheduling"
				)
				continue
			
			activity = frappe.get_doc({
				"doctype": "Salesforce Activity",
				"subject": f"Planned Call for {row.customer}",
				"activity_type": "Planned Call",
				"party_type": "Customer",
				"party": row.customer,
				"sales_person": mcp_doc.sales_person,
				"start_datetime": target_date,
				"docstatus": 0
			})
			activity.insert(ignore_permissions=True)
			
			# Increment the in-memory counter for the chosen date
			key = (mcp_doc.sales_person, str(target_date))
			daily_counts[key] = daily_counts.get(key, 0) + 1
			generated_count += 1
				
	if generated_count > 0:
		frappe.db.commit()
		
	return generated_count

