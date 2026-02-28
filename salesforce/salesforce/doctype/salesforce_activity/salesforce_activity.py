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
		
		# Fetch Party Name, Primary Address, and Primary Contact
		if self.party_type and self.party:
			if self.party_type == "Customer":
				self.party_name = frappe.db.get_value("Customer", self.party, "customer_name")
				address_name = frappe.db.get_value("Customer", self.party, "customer_primary_address")
				if address_name:
					addr = frappe.get_doc("Address", address_name)
					address_parts = filter(None, [addr.address_line1, addr.address_line2, addr.city])
					self.primary_address = ", ".join(address_parts)
				contact_name = frappe.db.get_value("Customer", self.party, "customer_primary_contact")
				if contact_name:
					con = frappe.get_doc("Contact", contact_name)
					contact_parts = filter(None, [con.first_name, con.last_name, con.mobile_no, con.email_id])
					self.primary_contact = " - ".join(contact_parts)
			elif self.party_type == "Lead":
				lead = frappe.get_doc("Lead", self.party)
				self.party_name = lead.lead_name or lead.company_name
				
				# Lead has built-in address and contact info usually
				address_parts = filter(None, [lead.address_line1, lead.address_line2, lead.city])
				self.primary_address = ", ".join(address_parts) if any(address_parts) else ""
				
				contact_parts = filter(None, [lead.mobile_no, lead.phone, lead.email_id])
				self.primary_contact = " - ".join(contact_parts) if any(contact_parts) else ""


	def before_submit(self):
		# Require at least one image before the document can be submitted
		if not self.images:
			frappe.throw(
				_("Please upload at least one image before submitting this activity."),
				title=_("Image Required")
			)
