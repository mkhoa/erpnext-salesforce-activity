# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SalesforceActivity(Document):
	def before_save(self):
		if not self.sales_person:
			# Auto-assign Sales Person based on the logged-in user
			employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
			if employee:
				sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
				if sales_person:
					self.sales_person = sales_person

	def before_submit(self):
		# Require at least one image before the document can be submitted
		if not self.images or len(self.images) == 0:
			frappe.throw(
				_("Please upload at least one image before submitting this activity."),
				title=_("Image Required")
			)
