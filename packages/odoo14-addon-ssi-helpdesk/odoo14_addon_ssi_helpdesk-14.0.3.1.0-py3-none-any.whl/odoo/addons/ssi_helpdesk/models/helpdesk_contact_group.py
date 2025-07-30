# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskContactGroup(models.Model):
    _name = "helpdesk_contact_group"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Helpdesk Contact Group"

    commercial_contact_id = fields.Many2one(
        string="Commercial Contact",
        comodel_name="res.partner",
        domain=[
            ("parent_id", "=", False),
        ],
        required=True,
    )
    contact_ids = fields.Many2many(
        string="Contacts",
        comodel_name="res.partner",
        relation="rel_helpdesk_contact_group_2_partner",
        column1="group_id",
        column2="partner_id",
        required=True,
    )

    @api.depends(
        "commercial_contact_id",
    )
    def onchange_contact_ids(self):
        self.contact_ids = [(5)]
