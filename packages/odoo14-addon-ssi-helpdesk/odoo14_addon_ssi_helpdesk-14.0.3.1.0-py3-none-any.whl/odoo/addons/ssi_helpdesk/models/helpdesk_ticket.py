# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class HelpdeskTicket(models.Model):
    _name = "helpdesk_ticket"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_terminate",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_ready",
    ]
    _description = "Helpdesk Ticket"

    # Multiple Approval Attribute
    _approval_from_state = "open"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,ready,open,confirm,done"

    _policy_field_order = [
        "ready_ok",
        "open_ok",
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "terminate_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_ready",
        "action_open",
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_ready",
        "dom_open",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_terminate",
        "dom_cancel",
    ]

    _create_sequence_state = "ready"

    title = fields.Char(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=True,
    )
    partner_id = fields.Many2one(
        string="Contact",
        comodel_name="res.partner",
        domain=[
            ("is_company", "=", False),
            ("parent_id", "!=", False),
        ],
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=True,
    )
    commercial_partner_id = fields.Many2one(
        string="Commercial Contact",
        comodel_name="res.partner",
        related="partner_id.commercial_partner_id",
        store=True,
    )
    contact_group_ids = fields.Many2many(
        string="Contact Group",
        comodel_name="helpdesk_contact_group",
        relation="rel_helpdesk_ticket_2_contact_group",
        column1="ticket_id",
        column2="group_id",
        copy=True,
    )
    additional_partner_ids = fields.Many2many(
        string="CC To",
        comodel_name="res.partner",
        relation="rel_helpdesk_ticket_2_additional_partner",
        column1="ticket_id",
        column2="partner_id",
        copy=True,
    )
    update_progress = fields.Boolean(
        string="Update Progress",
        default=True,
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="helpdesk_type",
        required=False,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=True,
    )
    type_category_id = fields.Many2one(
        string="Category",
        related=False,
        required=False,
        comodel_name="helpdesk_type_category",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=True,
    )

    @api.model
    def _default_date(self):
        return fields.Date.today()

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self._default_date(),
        copy=True,
    )
    duration_id = fields.Many2one(
        string="Duration",
        comodel_name="base.duration",
        copy=False,
    )
    date_deadline = fields.Date(
        string="Deadline",
        required=False,
        copy=False,
    )
    description = fields.Html(
        string="Description",
        readonly=False,
        copy=True,
    )
    communication_ids = fields.One2many(
        string="Communications",
        comodel_name="helpdesk_communication",
        inverse_name="ticket_id",
        copy=False,
    )
    starting_communication_id = fields.Many2one(
        string="# Starting Communication",
        comodel_name="helpdesk_communication",
        readonly=True,
        copy=False,
    )
    finishing_communication_id = fields.Many2one(
        string="# Finishing Communication",
        comodel_name="helpdesk_communication",
        readonly=True,
        copy=False,
    )
    latest_message_date = fields.Datetime(
        string="Latest Message Date",
        related="finishing_communication_id.latest_message_date",
        store=True,
    )
    latest_partner_message_date = fields.Datetime(
        string="Latest Partner Message Date",
        related="finishing_communication_id.latest_partner_message_date",
        store=True,
    )
    finishing_communication_state = fields.Selection(
        string="Finishing Communication State",
        related="finishing_communication_id.state",
        store=True,
    )
    duplicate_id = fields.Many2one(
        string="# Duplicate With",
        comodel_name="helpdesk_ticket",
        copy=False,
    )
    duplicate_ids = fields.One2many(
        string="Duplicates",
        comodel_name="helpdesk_ticket",
        inverse_name="duplicate_id",
        copy=False,
    )
    split_id = fields.Many2one(
        string="# Original Ticket",
        comodel_name="helpdesk_ticket",
        copy=False,
    )
    split_ids = fields.One2many(
        string="Split Into",
        comodel_name="helpdesk_ticket",
        inverse_name="split_id",
        copy=False,
    )
    resolution_documentation_ids = fields.One2many(
        string="Resolution Documentations",
        comodel_name="helpdesk_ticket.resolution_documentation",
        inverse_name="ticket_id",
    )
    resolution_documentation_state = fields.Selection(
        string="Resolution Documentation Status",
        selection=[
            ("no_need", "Not Needed"),
            ("open", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_resolution_documentation_state",
        store=True,
    )
    communication_draft_count = fields.Integer(
        string="Need Respond Count", store=True, compute="_compute_communication_count"
    )
    communication_open_count = fields.Integer(
        string="Waiting for Respond Count",
        store=True,
        compute="_compute_communication_count",
    )

    @api.model
    def _get_policy_field(self):
        res = super(HelpdeskTicket, self)._get_policy_field()
        policy_field = [
            "ready_ok",
            "open_ok",
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "done_ok",
            "cancel_ok",
            "restart_ok",
            "terminate_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.depends(
        "resolution_documentation_ids",
        "resolution_documentation_ids.state",
    )
    def _compute_resolution_documentation_state(self):
        for record in self:
            result = "no_need"

            count_req = len(record.resolution_documentation_ids)

            if count_req > 0:
                result = "done"
                for req in record.resolution_documentation_ids:
                    if req.state == "open":
                        result = "open"

            record.resolution_documentation_state = result

    @api.onchange(
        "partner_id",
        "contact_group_ids",
    )
    def onchange_additional_partner_ids(self):
        self.additional_partner_ids = [(6, 0, [])]

        if self.contact_group_ids:
            contact_groups = self.contact_group_ids.mapped("contact_ids")
            # TODO: This is not working. Why?
            contact_groups = contact_groups - self.partner_id
            self.additional_partner_ids = [(6, 0, contact_groups.ids)]

    @api.onchange(
        "type_category_id",
    )
    def onchange_type_id(self):
        self.type_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_title(self):
        result = ""
        if self.type_id and self.type_category_id.auto_title:
            result = "%s - %s" % (self.type_category_id.name, self.type_id.name)
        self.title = result

    @api.onchange(
        "partner_id",
    )
    def onchange_contact_group_ids(self):
        self.contact_group_ids = [(6, 0, [])]

    @api.onchange(
        "type_id",
    )
    def onchange_duration_id(self):
        self.duration_id = False
        if self.type_id:
            self.duration_id = self.type_id.duration_id

    @api.onchange(
        "duration_id",
        "date",
    )
    def onchange_date_deadline(self):
        self.date_deadline = False
        if self.duration_id:
            self.date_deadline = self.duration_id.get_duration(self.date)

    @api.model_create_multi
    def create(self, values):
        _super = super(HelpdeskTicket, self)
        results = _super.create(values)
        for result in results:
            result._create_sequence()
        return result

    def action_create_finishing_communication(self):
        for record in self.sudo():
            result = record._create_finishing_communication()
        return result

    def action_create_updating_communication(self):
        for record in self.sudo():
            result = record._create_updating_communication()
        return result

    def action_open_communication(self):
        for record in self.sudo():
            result = record._open_communication()
        return result

    def action_open_split(self):
        for record in self.sudo():
            result = record._open_split()
        return result

    def _open_split(self):
        waction = self.env.ref("ssi_helpdesk.helpdesk_ticket_action").read()[0]
        new_context = {
            "default_split_id": self.id,
        }
        waction.update(
            {
                "view_mode": "tree,form",
                "domain": [("split_id", "=", self.id)],
                "context": new_context,
            }
        )
        return waction

    def _open_communication(self):
        waction = self.env.ref("ssi_helpdesk.helpdesk_communication_action").read()[0]
        waction.update(
            {
                "view_mode": "tree,form",
                "domain": [("ticket_id", "=", self.id)],
            }
        )
        return waction

    def _create_finishing_communication(self):
        HC = self.env["helpdesk_communication"]
        hc = HC.create(self._prepare_create_finishing_communication())
        partner_ids = (self.additional_partner_ids + self.partner_id).ids
        hc.message_subscribe(partner_ids)
        self.write(
            {
                "finishing_communication_id": hc.id,
            }
        )
        return {
            "name": hc.title,
            "view_mode": "form",
            "res_model": "helpdesk_communication",
            "res_id": hc.id,
            "type": "ir.actions.act_window",
        }

    def _create_updating_communication(self):
        self.ensure_one()
        HC = self.env["helpdesk_communication"]
        hc = HC.create(self._prepare_create_updating_communication())
        partner_ids = (self.additional_partner_ids + self.partner_id).ids
        hc.message_subscribe(partner_ids)
        return {
            "name": hc.title,
            "view_mode": "form",
            "res_model": "helpdesk_communication",
            "res_id": hc.id,
            "type": "ir.actions.act_window",
        }

    def _prepare_create_finishing_communication(self):
        return {
            "partner_id": self.partner_id.id,
            "title": self.title,
            "ticket_id": self.id,
        }

    def _prepare_create_updating_communication(self):
        title = "Ticket status update - %s - %s" % (self.name, fields.Date.today())
        return {
            "partner_id": self.partner_id.id,
            "title": title,
            "ticket_id": self.id,
        }

    @api.depends("communication_ids", "communication_ids.state")
    def _compute_communication_count(self):
        for record in self:
            record.communication_draft_count = len(
                record.communication_ids.filtered(lambda x: x.state == "draft")
            )
            record.communication_open_count = len(
                record.communication_ids.filtered(lambda x: x.state == "open")
            )

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
