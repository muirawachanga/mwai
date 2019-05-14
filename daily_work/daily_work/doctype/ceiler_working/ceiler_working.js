// Copyright (c) 2019, steve and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ceiler Working', {
    setup: function(frm) {
    		frm.add_fetch('employee', 'employee_name', 'employee_name')
    		frm.fields_dict.employee.get_query = function() {
    			return {
    				filters:{
    					'status': 'Active'
    				}
    			}
    		}

    },
	refresh: function(frm) {
         if (frm.doc.payment_status == 'Pending' && frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Make Payment"), function () {
                frm.events.make_payment(frm);
            }).addClass("btn-primary");
         }

	},
	update_warehouse: function(frm){
	    frm.fields_dict.update_warehouse_btn.$input.addClass("btn-primary");
        frm.refresh()

	},
	update_warehouse_func: function(frm){
        return frappe.call({
            method: 'get_provided_items',
            doc: frm.doc
        })
	},
	update_warehouse_btn: function(frm){
	    if(frm.doc.update_warehouse){
	        frm.events.update_warehouse_func(frm);

	    }

	},
	make_payment: function(frm){
        return frappe.call({
            method: 'create_payment_journal',
            doc: frm.doc,
           callback: function(r, rt) {
                 cur_frm.reload_doc()
           }
        })

	},
	total: function(frm){
	    if(frm.doc.total) {
	        return frappe.call({
	            method: 'set_net_pay',
	            doc: frm.doc
	        })
	    }

	},
	employee: function(frm) {
	    if(frm.doc.employee) {
	        return frappe.call({
	           method: 'create_warehouse',
	           doc: frm.doc,
	           callback: function(r, rt) {
               		frm.refresh()
               }
	        })
	    }
	}
})
frappe.ui.form.on("Destroyed Items", {
    destroyed_items_remove: function(frm) {
        calculate_total_amount(frm);
    },
    quantity: function(frm, cdt, cdn){
          var child = locals[cdt][cdn]
          if (child.quantity){
              var total = child.quantity * child.cost_charged
              frappe.model.set_value(cdt, cdn, "total_amount", total)
          }
          calculate_total_amount(frm)
     },

    cost_charged: function(frm, cdt, cdn){
        var child = locals[cdt][cdn]
        if (child.quantity){
            var total = child.quantity * child.cost_charged
            frappe.model.set_value(cdt, cdn, "total_amount", total)
        }
        calculate_total_amount(frm)
    }

})
frappe.ui.form.on("Bundles", {
    bundles_remove: function(frm) {
        calculate_total_bundle(frm);
    },
    quantity: function(frm){
          calculate_total_bundle(frm)
     }

})
cur_frm.cscript.item = function(doc, cdt, cdn) {
    if (frappe.model.get_value(cdt, cdn, "item")) {
        frappe.model.set_value(cdt, cdn, "check", 1);
        cur_frm.fields_dict["items"].grid.grid_rows_by_docname[cdn].fields_dict["check"].refresh();
    }
}
var calculate_total_amount = function(frm) {
    var tl = frm.doc.destroyed_items || [];
    var total_amount = 0;
    for(var i=0; i<tl.length; i++) {
        if (tl[i].total_amount) {
            total_amount += tl[i].total_amount;
        }
    }
    frm.set_value("total_deduction", total_amount);
    refresh_field('total_deduction')
}
var calculate_total_bundle = function(frm) {
    var tl = frm.doc.bundles || [];
    var total_bundles = 0;
    for(var i=0; i<tl.length; i++) {
        if (tl[i].quantity) {
            total_bundles += tl[i].quantity;
        }
    }
    frm.set_value("total", total_bundles);
    refresh_field('total')
}
