# -*- coding: utf-8 -*-
# Copyright (c) 2019, steve and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import nowdate
from frappe.model.document import Document

class OperatorCore(Document):

	def validate(self):
		core = load_configuration('default_core_item')
		core_warehouse = load_configuration('warehouse_produced_core')
		sold_to_warehouse = load_configuration('warehouse_workin_progress')
		waste_warehouse = load_configuration('warehouse_destroyed_materials')
		waste_item = load_configuration('waste')
		transfer_material('Stock Entry', core_warehouse, core, self.core_produced,  waste_item, waste_warehouse, self.core_destroyed, self.core_sold, sold_to_warehouse)

def transfer_material(parent, t_warehouse, core, core_qty, waste_item, waste_warehouse, waste_qty, qty_sold =None, s_warehouse=None):

	core_entry = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Receipt",
		"company": erpnext.get_default_company()
	})
	core_sold = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Transfer",
		"company": erpnext.get_default_company()
	})
	waste_entry = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Receipt",
		"company": erpnext.get_default_company()
	})
	core_entry.append("items",
						 {"item_code": core,
						  "t_warehouse": t_warehouse,
						  "qty": core_qty,
						  "uom": "Nos",
						  "conversion_factor": 1.000000,
						  "stock_uom": "Nos",
						  "transfer_qty": core_qty})
	core_sold.append("items",
					  {"item_code": core,
					   "s_warehouse": t_warehouse, # warehouse are interchanged to allow the transfer
					   "t_warehouse": s_warehouse,
					   "qty": qty_sold,
					   "uom": "Nos",
					   "conversion_factor": 1.000000,
					   "stock_uom": "Nos",
					   "transfer_qty": qty_sold})
	waste_entry.append("items",
					   {"item_code": waste_item,
						"t_warehouse": waste_warehouse, # this is source warehouse for the issue
						"qty": waste_qty,
						"uom": "Kg",
						"conversion_factor": 1.000000,
						"stock_uom": "Kg",
						"transfer_qty": waste_qty})
	core_entry.insert()
	core_entry.submit()
	if qty_sold:
		core_sold.insert()
		core_sold.submit()
	if waste_qty:
		waste_entry.insert()
		waste_entry.submit()
	frappe.msgprint(_('The information has been saved successfully. Thank you'))


def load_configuration(name, default=None):
	val = frappe.db.get_single_value('Daily Default Setting', name)
	if val is None:
		val = default
	return val
