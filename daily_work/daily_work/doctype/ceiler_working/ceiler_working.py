# -*- coding: utf-8 -*-
# Copyright (c) 2019, steve and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import erpnext
from frappe.utils import nowdate, flt
from frappe.model.document import Document


class CeilerWorking(Document):

	def	validate(self):
		self.create_warehouse()
		self.set_net_pay()

	def on_submit(self):

		if not self.update_warehouse:
			frappe.throw(_('You must tick update warehouse check'))

	def create_warehouse(self):
		company = erpnext.get_default_company()
		abbr = frappe.get_value('Company', company, 'abbr')
		warehouse = frappe.get_doc({
			"doctype": "Warehouse",
			"warehouse_name": self.employee_name,
			"parent_warehouse": "All Warehouses - {0}".format(abbr)
		})
		# The System Manager might not have permission to create warehouse hence the flag
		if frappe.db.exists('Warehouse', self.employee_name+ ' - {0}'.format(abbr)):
			self.warehouse = self.employee_name + ' - {0}'.format(abbr)
		else:
			warehouse.flags.ignore_permissions = True
			warehouse.insert()
			self.warehouse = self.employee_name + ' - {0}'.format(abbr)

	def set_net_pay(self):
		charge_bundle = load_configuration('amount_bundle')
		if self.total:
			bundle_pay = flt(charge_bundle) * flt(self.total)
			self.bundle_pay = bundle_pay
			net_pay = bundle_pay - flt(self.total_deduction)
			self.net_payable_amount = net_pay

	def get_provided_items(self):
		items_list = get_provided_items(self)
		if items_list:
			default_warehouse = load_configuration('item_warehouse')
			item_provided = self.append('provided_items', {})
			for data in items_list:
				if data: # remove row witho the data
					qty = data.quantity
					item = data.item
					transfer_provided_items('Stock Entry', self.warehouse, qty, item, default_warehouse)
					continue

		if self.bundles:
			bundle_item = load_configuration('default_tissue')
			warehouse = load_configuration('warehouse_tissue')
			for data in get_bundles(self):
				qty = data.quantity * 40.0
				transfer_bundles('Stock Entry', warehouse, qty, bundle_item)

		if self.destroyed_items:
			destroyed_warehouse = load_configuration('warehouse_destroyed_materials')
			destroyed_list = get_destroyed_items(self)
			if destroyed_list:
				for data in destroyed_list:
					item = data.item
					qty = data.quantity
					transfer_destroyed('Stock Entry', destroyed_warehouse, qty, item, self.warehouse)
		frappe.msgprint(_('The information has been saved successfully. Thank you'))

	def create_payment_journal(self):
        
		salary_account = load_configuration('salary_account')
		pay_account = load_configuration('pay_account')
		journal_entry = frappe.new_doc('Journal Entry')
		journal_amt = flt(self.net_payable_amount)
		if journal_amt == 0.0:
			return
		cr_entry = journal_entry.append("accounts", {})
		cr_entry.account = pay_account
		cr_entry.credit_in_account_currency = journal_amt

		dr_entry = journal_entry.append("accounts", {})
		dr_entry.account = salary_account
		dr_entry.debit_in_account_currency = journal_amt
		# dr_entry.reference_name = self.name //TODO make a query in the custom script
		journal_entry.set("posting_date", nowdate())
		journal_entry.set("user_remark", "This is confirmation of the payment done to {0}".format(self.employee_name))
		journal_entry.flags.ignore_permissions = True
		journal_entry.save()
		journal_entry.submit()
		lr = frappe.get_doc('Ceiler Working', self.name)
		lr.set('payment_status', 'Settled')
		lr.db_update()
		frappe.msgprint(_('The payment made successfully for {0}'.format(self.employee_name)))

def load_configuration(name, default=None):

	val = frappe.db.get_single_value('Daily Default Setting', name)
	if val is None:
		val = default
	return val

def transfer_provided_items(parent, t_warehouse, item_qty, item_code, s_warehouse):

	employee_transfer = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Transfer",
		"company": erpnext.get_default_company()
	})
	employee_transfer.append("items",
					 {"item_code": item_code,
					  "s_warehouse": s_warehouse, # warehouse are interchanged to allow the transfer
					  "t_warehouse": t_warehouse,
					  "qty": item_qty,
					  "uom": "Nos",
					  "conversion_factor": 1.000000,
					  "stock_uom": "Nos",
					  "transfer_qty": item_qty})
	employee_transfer.insert()
	employee_transfer.submit()

def transfer_bundles(parent, t_warehouse, item_qty, item_code, s_warehouse=None):
	employee_transfer = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Receipt",
		"company": erpnext.get_default_company()
	})
	employee_transfer.append("items",
							 {"item_code": item_code,
							  "s_warehouse": s_warehouse, # warehouse are interchanged to allow the transfer
							  "t_warehouse": t_warehouse,
							  "qty": item_qty,
							  "uom": "Nos",
							  "conversion_factor": 1.000000,
							  "stock_uom": "Nos",
							  "transfer_qty": item_qty})
	employee_transfer.insert()
	employee_transfer.submit()

def transfer_destroyed(parent, t_warehouse, item_qty, item_code, s_warehouse=None):
	employee_transfer = frappe.get_doc({
		"doctype": parent,
		"posting_date": nowdate(),
		"purpose": "Material Transfer",
		"company": erpnext.get_default_company()
	})
	employee_transfer.append("items",
							 {"item_code": item_code,
							  "s_warehouse": s_warehouse, # warehouse are interchanged to allow the transfer
							  "t_warehouse": t_warehouse,
							  "qty": item_qty,
							  "uom": "Nos",
							  "conversion_factor": 1.000000,
							  "stock_uom": "Nos",
							  "transfer_qty": item_qty})
	employee_transfer.insert()
	employee_transfer.submit()

def get_provided_items(self):
	"""tabItem Provided, tabCeiler Working"""
	provided_items = """select ip.item, ip.quantity from `tabItem Provided` ip, `tabCeiler Working` cw where cw.name = ip.parent
						and cw.name = '%s';""" %(self.name)
	if provided_items:
		return frappe.db.sql(provided_items, as_dict=1)
	else:
		return 0

def get_bundles(self):
	"""tabBundles, tabCeiler Working"""
	bundle = """select bu.quantity from `tabBundles` bu, `tabCeiler Working` cw where cw.name = bu.parent
						and cw.name = '%s';""" %(self.name)
	if bundle:
		return frappe.db.sql(bundle, as_dict=1)
	else:
		return 0

def get_destroyed_items(self):
	"""tabDestroyed Items, tabCeiler Working"""
	destroyed_item = """select di.item, di.quantity from `tabDestroyed Items` di, `tabCeiler Working` cw where cw.name = di.parent
						and cw.name = '%s';""" %(self.name)
	if destroyed_item:
		return frappe.db.sql(destroyed_item, as_dict=1)
	else:
		return 0





