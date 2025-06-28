import frappe
import json
from frappe import _

def get_context(context):
	"""Get context for the Aida AI dashboard page"""
	context.no_cache = 1
	context.show_sidebar = False
	
	# Check if user is logged in
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to access Aida AI Dashboard"), frappe.PermissionError)
	
	# Get user sessions
	context.sessions = frappe.get_all(
		"Aida AI Session",
		filters={"status": "Active"},
		fields=["name", "session_name", "company_name", "creation", "total_leads", "emails_sent"]
	)
	
	# Get API base URL from site config or default
	api_base = frappe.conf.get("aida_api_base", "http://localhost:8000")
	context.api_base = api_base
	
	return context

@frappe.whitelist()
def create_session(session_data):
	"""Create a new Aida AI session"""
	try:
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
		frappe.db.commit()
		
		return {
			"success": True,
			"session_id": session.name,
			"message": "Session created successfully"
		}
		
	except Exception as e:
		frappe.log_error(f"Error creating Aida AI session: {str(e)}")
		return {
			"success": False,
			"message": f"Error creating session: {str(e)}"
		}

@frappe.whitelist()
def get_session_details(session_id):
	"""Get detailed session information"""
	try:
		session = frappe.get_doc("Aida AI Session", session_id)
		
		return {
			"success": True,
			"data": {
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
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting session details: {str(e)}")
		return {
			"success": False,
			"message": f"Error getting session details: {str(e)}"
		}

@frappe.whitelist()
def update_session_stats(session_id, leads_generated=0, emails_sent=0):
	"""Update session statistics"""
	try:
		session = frappe.get_doc("Aida AI Session", session_id)
		
		if leads_generated:
			session.total_leads = (session.total_leads or 0) + int(leads_generated)
		if emails_sent:
			session.emails_sent = (session.emails_sent or 0) + int(emails_sent)
		
		session.save(ignore_permissions=True)
		frappe.db.commit()
		
		return {
			"success": True,
			"message": "Statistics updated successfully"
		}
		
	except Exception as e:
		frappe.log_error(f"Error updating session stats: {str(e)}")
		return {
			"success": False,
			"message": f"Error updating statistics: {str(e)}"
		}