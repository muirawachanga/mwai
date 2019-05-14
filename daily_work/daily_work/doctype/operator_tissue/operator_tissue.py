# -*- coding: utf-8 -*-
# Copyright (c) 2019, steve and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import nowdate
from frappe.model.document import Document

class OperatorTissue(Document):
	def validate(self):
		core = load_configuration('default_core_item')
		waste_warehouse = load_configuration('warehouse_destroyed_materials')
		waste_item = load_configuration('waste')
		core_store_warehouse = load_configuration('warehouse_workin_progress')
		transfer_material('Stock Entry', core_store_warehouse, waste_warehouse, core, self.core_used, waste_item, self.material_destroyed)

def transfer_material(parent, t_warehouse, waste_warehouse, core, core_qty, waste_item, waste_qty):

	core_removal = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Issue",
		"company": erpnext.get_default_company()
	})
	waste_entry = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Receipt",
		"company": erpnext.get_default_company()
	})
	core_removal.append("items",
					  {"item_code": core,
					   "s_warehouse": t_warehouse,
					   "qty": core_qty,
					   "uom": "Nos",
					   "conversion_factor": 1.000000,
					   "stock_uom": "Nos",
					   "transfer_qty": core_qty})

	waste_entry.append("items",
						{"item_code": waste_item,
						 "t_warehouse": waste_warehouse, # this is source warehouse for the issue
						 "qty": waste_qty,
						 "uom": "Kg",
						 "conversion_factor": 1.000000,
						 "stock_uom": "Kg",
						 "transfer_qty": waste_qty})

	core_removal.insert()
	core_removal.submit()
	if waste_qty:
		waste_entry.insert()
		waste_entry.submit()
	frappe.msgprint(_('The information has been saved successfully. Thank you'))


def load_configuration(name, default=None):
	val = frappe.db.get_single_value('Daily Default Setting', name)
	if val is None:
		val = default
	return val
