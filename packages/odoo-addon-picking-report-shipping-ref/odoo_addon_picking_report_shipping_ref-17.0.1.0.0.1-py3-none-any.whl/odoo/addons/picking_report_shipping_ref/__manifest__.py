# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Picking Report Shipping Ref",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "summary": "Adds a shipping reference label to delivery orders.",
    "author": "Sygel, Odoo Community Association (OCA)",
    "website": "https://github.com/sygel-technology/sy-stock-logistics-reporting",
    "depends": ["stock"],
    "data": [
        "views/res_config_settings_views.xml",
        "report/report_deliveryslip.xml",
        "report/report_stock_picking_operations.xml",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
