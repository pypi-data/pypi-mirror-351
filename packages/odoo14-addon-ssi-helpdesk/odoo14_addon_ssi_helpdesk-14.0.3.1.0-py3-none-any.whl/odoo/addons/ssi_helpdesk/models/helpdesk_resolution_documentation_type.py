# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HelpdeskResolutionDocumentationType(models.Model):
    _name = "helpdesk_resolution_documentation_type"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Helpdesk Resolution Documentation Type"
