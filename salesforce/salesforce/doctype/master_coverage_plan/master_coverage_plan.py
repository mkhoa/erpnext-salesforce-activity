import frappe
import calendar
from datetime import timedelta
from frappe.utils import today, getdate
from frappe.model.document import Document


class MasterCoveragePlan(Document):
	pass


def _get_date_context():
	"""Return a dict of common date calculations used for generation logic."""
	current_date = getdate(today())
	return {
		"current_date": current_date,
		"current_weekday": calendar.day_name[current_date.weekday()],
		"week_of_month": (current_date.day - 1) // 7 + 1,
		"month_of_quarter": (current_date.month - 1) % 3 + 1,
	}


@frappe.whitelist()
def generate_planned_calls_on_demand(mcp_name):
	mcp_doc = frappe.get_doc("Master Coverage Plan", mcp_name)
	ctx = _get_date_context()
	return _process_mcp(mcp_doc, **ctx)


@frappe.whitelist()
def generate_planned_calls():
	ctx = _get_date_context()
	total = 0
	for mcp in frappe.get_all("Master Coverage Plan", fields=["name"]):
		mcp_doc = frappe.get_doc("Master Coverage Plan", mcp.name)
		total += _process_mcp(mcp_doc, **ctx)
	return total


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
	# Build a set of preferred calendar.day_name values from the checkboxes
	preferred_days = {
		day for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		if getattr(row, day.lower(), 0) == 1
	}

	candidate = start_date
	for _ in range(max_days_ahead):
		candidate = candidate + timedelta(days=1)
		weekday_name = calendar.day_name[candidate.weekday()]
		if weekday_name in preferred_days and _get_daily_count(sales_person, candidate, daily_counts) < DAILY_VISIT_CAP:
			return candidate

	return None  # No slot found within the window


def _process_mcp(mcp_doc, current_date, current_weekday, week_of_month, month_of_quarter):
	generated_count = 0
	# Per-run in-memory cache: (sales_person, date_str) -> count
	daily_counts = {}

	for row in mcp_doc.customers:
		# Check if the checkbox for today's weekday is checked
		is_preferred_day = getattr(row, current_weekday.lower(), 0) == 1
		freq = row.visit_frequency

		if freq != "D1" and not is_preferred_day:
			continue

		should_visit = (
			freq == "D1"
			or (freq == "M1" and week_of_month == 1)
			or (freq == "M2" and week_of_month in (1, 3))
			or (freq == "M4" and week_of_month <= 4)
			or (freq == "Q1" and month_of_quarter == 1 and week_of_month == 1)
			or (freq == "Q2" and month_of_quarter in (1, 2) and week_of_month == 1)
		)

		if not should_visit:
			continue

		# Skip if a Planned Call already exists for this customer today
		if frappe.db.exists("Salesforce Activity", {
			"sales_person": mcp_doc.sales_person,
			"party_type": "Customer",
			"party": row.customer,
			"activity_type": "Planned Call",
			"start_datetime": ["like", f"{current_date}%"],
			"docstatus": ["in", [0, 1]]
		}):
			continue

		# Determine target date, respecting the daily cap
		target_date = current_date
		if _get_daily_count(mcp_doc.sales_person, target_date, daily_counts) >= DAILY_VISIT_CAP:
			target_date = _find_next_available_date(row, mcp_doc.sales_person, current_date, daily_counts)

		if target_date is None:
			frappe.log_error(
				f"No slot for {row.customer} ({mcp_doc.sales_person}) within 60 days.",
				"Planned Call Scheduling"
			)
			continue

		frappe.get_doc({
			"doctype": "Salesforce Activity",
			"subject": f"Planned Call for {row.customer}",
			"activity_type": "Planned Call",
			"party_type": "Customer",
			"party": row.customer,
			"sales_person": mcp_doc.sales_person,
			"start_datetime": target_date,
		}).insert(ignore_permissions=True)

		# Update in-memory counter
		key = (mcp_doc.sales_person, str(target_date))
		daily_counts[key] = daily_counts.get(key, 0) + 1
		generated_count += 1

	if generated_count > 0:
		frappe.db.commit()

	return generated_count
