# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskTicketResolutionDocumentation(models.Model):
    _name = "helpdesk_ticket.resolution_documentation"
    _description = "Helpdesk Ticket Resolution Documentation"
    _order = "ticket_id, sequence, id"

    ticket_id = fields.Many2one(
        string="# Helpdesk Ticket",
        comodel_name="helpdesk_ticket",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=10,
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="helpdesk_resolution_documentation_type",
        ondelete="restrict",
    )
    name = fields.Char(
        string="Documentation",
        required=True,
    )
    url = fields.Char(
        string="URL",
        required=False,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("open", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_state",
        store=True,
    )

    @api.depends(
        "url",
    )
    def _compute_state(self):
        for record in self:
            result = "open"
            if record.url:
                result = "done"
            record.state = result

    @api.onchange(
        "type_id",
    )
    def onchange_name(self):
        self.name = False
        if self.type_id:
            self.name = self.type_id.name
