# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_default_name(self):
        return _("New Approval Request")

    document_id = fields.Many2one('documents.document', string='Document')
    download_id = fields.Many2one('download.documents', string='Download')
    approve_sequence = fields.Boolean(default=True)
    sequence = fields.Integer(default=1)
    approve_sequence_bypass = fields.Boolean(default=True)
    has_forward = fields.Boolean(default=True)
    approve_request = fields.Boolean(string='Approve Request')
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=False
    )
    notify_reminder_delay = fields.Integer(default=1)

    @api.constrains('notify_reminder_delay')
    def _check_notify_reminder_delay_rule(self):
            for record in self:
                if record.notify_reminder_delay <= 0:
                    raise UserError(_("Notify remender delay greater than 0"))
    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.extend(["documents.document", "download.documents"])
        return res

    @api.onchange('get_manager_of_department')
    def check_click_role(self):
        if self.get_manager_of_department:
            self.get_head_of_department = False

    @api.onchange('get_head_of_department')
    def check_click_head_department(self):
        if self.get_head_of_department:
            self.get_manager_of_department = False
