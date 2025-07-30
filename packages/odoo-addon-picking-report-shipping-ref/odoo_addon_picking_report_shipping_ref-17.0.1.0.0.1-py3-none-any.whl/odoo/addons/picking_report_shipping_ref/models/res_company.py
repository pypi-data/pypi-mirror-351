# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    delivery_shipping_ref_label = fields.Char(
        string="Delivery Shipping Ref. Label",
        translate=True,
    )
