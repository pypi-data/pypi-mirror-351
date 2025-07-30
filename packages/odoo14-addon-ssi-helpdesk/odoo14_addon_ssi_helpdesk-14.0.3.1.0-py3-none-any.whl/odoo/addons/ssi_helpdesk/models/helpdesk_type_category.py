# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTypeCategory(models.Model):
    _name = "helpdesk_type_category"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Helpdesk Type Category"

    auto_title = fields.Boolean(
        string="Auto Generate Title",
    )
