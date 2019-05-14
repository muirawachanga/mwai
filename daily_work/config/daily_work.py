from __future__ import unicode_literals

from frappe import _


def get_data():
    return [
        {
            "label": _("Daily work"),
            "icon": "icon-star",
            "items": [
                {
                    "type": "doctype",
                    "name": "Ceiler Working",
                    "description": _("Timesheets for daily details provision.")
                },
                {
                    "type": "doctype",
                    "name": "Operator Core",
                    "description": _("Operator core for daily details provision.")
                },
                {
                    "type": "doctype",
                    "name": "Operator Tissue",
                    "description": _("Operator Tissue for daily details provision.")
                }
            ]
        },
        {
            "label": _("Standard Reports"),
            "icon": "icon-list",
            "items": [
                {
                    "type": "report",
                    "name": "Daily Timesheets Summary",
                    "doctype": "Daily Work",
                    "is_query_report": True,
                }
            ]
        },
        {
            "label": _("Daily Setting"),
            "icon": "icon-star",
            "items": [
                {
                    "type": "doctype",
                    "name": "Daily Default Setting",
                    "description": _("Daily Default Setting for the system")
                }

            ]
        }
    ]