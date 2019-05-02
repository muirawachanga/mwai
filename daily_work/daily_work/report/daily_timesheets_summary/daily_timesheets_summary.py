# Copyright (c) 2013, steve and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions

def execute(filters=None):
	if not filters:
		filters = {}
	elif filters.get("from_date") or filters.get("to_date"):
		filters["from_time"] = "00:00:00"
		filters["to_time"] = "24:00:00"

	columns = get_column()
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)

	return columns, data

def get_column():
	return [_("Timesheets") + ":Link/Timesheets:120", _("Employee") + "::150", _("Employee Name") + "::150",
			_("From Datetime") + "::140", _("To Datetime") + "::140", _("Bundles") + "::70",
			_("Activity Type") + "::120", _("Task") + ":Link/Task:150",
			_("Project") + ":Link/Project:120", _("Status") + "::70"]

def get_data(conditions, filters):
	time_sheet = frappe.db.sql(""" select `tabTimesheets`.name, `tabTimesheets`.employee, `tabTimesheets`.employee_name,
		`tabTimesheet Details`.from_time, `tabTimesheet Details`.to_time, `tabTimesheet Details`.hours,
		`tabTimesheet Details`.activity_type, `tabTimesheet Details`.task, `tabTimesheet Details`.project,
		`tabTimesheets`.status from `tabTimesheet Details`, `tabTimesheets` where
		`tabTimesheet Details`.parent = `tabTimesheets`.name and %s order by `tabTimesheets`.name"""%(conditions), filters, as_list=1)

	return time_sheet

def get_conditions(filters):
	conditions = "`tabTimesheets`.docstatus = 1"
	if filters.get("from_date"):
		conditions += " and `tabTimesheet Details`.from_time >= timestamp(%(from_date)s, %(from_time)s)"
	if filters.get("to_date"):
		conditions += " and `tabTimesheet Details`.to_time <= timestamp(%(to_date)s, %(to_time)s)"

	match_conditions = build_match_conditions("Timesheets")
	if match_conditions:
		conditions += " and %s" % match_conditions

	return conditions