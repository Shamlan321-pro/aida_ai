# Copyright (c) 2024, Aida AI Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import requests
from datetime import datetime

class AidaAISession(Document):
	def before_insert(self):
		"""Set default values before inserting"""
		self.created_by = frappe.session.user
		self.creation_date = datetime.now()
		
		# Auto-generate session name if not provided
		if not self.session_name:
			self.session_name = f"{self.company_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

	def validate(self):
		"""Validate the session configuration"""
		# Validate ERPNext URL format
		if self.erpnext_url and not (self.erpnext_url.startswith('http://') or self.erpnext_url.startswith('https://')):
			frappe.throw("ERPNext URL must start with http:// or https://")
		
		# Ensure at least one email template exists
		if not self.email_templates:
			self.add_default_email_templates()

	def add_default_email_templates(self):
		"""Add default email templates if none exist"""
		default_templates = [
			{
				"template_name": "Meeting Request",
				"template_type": "meeting",
				"subject": "Quick chat about {company_name}?",
				"body": "Hi {contact_name},\n\nI noticed {company_name} is in the {industry} space. We help companies like yours {value_proposition}.\n\nWould you be open to a brief 15-minute call to discuss how we can help {company_name}?\n\nBest regards,\n{sender_name}",
				"tone": "professional"
			},
			{
				"template_name": "Product Demo",
				"template_type": "product",
				"subject": "See how {our_company} can help {company_name}",
				"body": "Hello {contact_name},\n\nI hope this email finds you well. I'm reaching out because {company_name} seems like a perfect fit for our {main_service}.\n\n{value_proposition}\n\nWould you be interested in a quick demo to see how we can help {company_name}?\n\nBest,\n{sender_name}",
				"tone": "friendly"
			}
		]
		
		for template in default_templates:
			self.append("email_templates", template)

	def get_api_config(self):
		"""Get configuration for API calls"""
		return {
			"erpnext_config": {
				"url": self.erpnext_url,
				"username": self.erpnext_username,
				"password": self.get_password("erpnext_password")
			},
			"company_profile": {
				"name": self.company_name,
				"description": self.company_description,
				"industry": self.company_industry,
				"website": self.company_website,
				"offers": self.offers.split(',') if self.offers else [],
				"value_proposition": self.value_proposition
			},
			"email_templates": [
				{
					"name": template.template_name,
					"type": template.template_type,
					"subject": template.subject,
					"body": template.body,
					"tone": template.tone
				} for template in self.email_templates
			]
		}

	def update_statistics(self, leads_generated=0, emails_sent=0):
		"""Update session statistics"""
		if leads_generated:
			self.total_leads = (self.total_leads or 0) + leads_generated
		if emails_sent:
			self.emails_sent = (self.emails_sent or 0) + emails_sent
		
		self.save(ignore_permissions=True)

@frappe.whitelist()
def get_session_list():
	"""Get list of active sessions for current user"""
	sessions = frappe.get_all(
		"Aida AI Session",
		filters={"status": "Active"},
		fields=["name", "session_name", "company_name", "creation", "total_leads", "emails_sent"]
	)
	return sessions

@frappe.whitelist()
def get_session_details(session_id):
	"""Get detailed session information"""
	session = frappe.get_doc("Aida AI Session", session_id)
	return {
		"session_id": session.name,
		"session_name": session.session_name,
		"company_profile": {
			"name": session.company_name,
			"description": session.company_description,
			"industry": session.company_industry,
			"website": session.company_website,
			"offers": session.offers.split(',') if session.offers else [],
			"value_proposition": session.value_proposition
		},
		"email_templates": [
			{
				"name": template.template_name,
				"type": template.template_type,
				"subject": template.subject,
				"body": template.body,
				"tone": template.tone
			} for template in session.email_templates
		],
		"statistics": {
			"total_leads": session.total_leads or 0,
			"emails_sent": session.emails_sent or 0,
			"open_rate": session.open_rate or 0,
			"response_rate": session.response_rate or 0
		}
	}

@frappe.whitelist()
def create_session_from_api(session_data):
	"""Create a new session from API data"""
	if isinstance(session_data, str):
		session_data = json.loads(session_data)
	
	# Create new session document
	session = frappe.new_doc("Aida AI Session")
	
	# Set ERPNext configuration
	erpnext_config = session_data.get("erpnext_config", {})
	session.erpnext_url = erpnext_config.get("url")
	session.erpnext_username = erpnext_config.get("username")
	session.erpnext_password = erpnext_config.get("password")
	
	# Set company profile
	company_profile = session_data.get("company_profile", {})
	session.company_name = company_profile.get("name")
	session.company_description = company_profile.get("description")
	session.company_industry = company_profile.get("industry")
	session.company_website = company_profile.get("website")
	session.value_proposition = company_profile.get("value_proposition")
	session.offers = ", ".join(company_profile.get("offers", []))
	
	# Add email templates
	email_templates = session_data.get("email_templates", [])
	for template in email_templates:
		session.append("email_templates", {
			"template_name": template.get("name"),
			"template_type": template.get("type"),
			"subject": template.get("subject"),
			"body": template.get("body"),
			"tone": template.get("tone", "professional")
		})
	
	session.insert()
	return session.name