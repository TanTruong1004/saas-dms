# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from random import randint


class DownloadDocuments(models.Model):
    _name = 'download.documents'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'tier.validation']
    _description = 'Download Documents'
    _state_field = "state"
    _state_from = ["draft", "in_progress"]
    _state_to = ["confirmed"]
    _cancel_state = "canceled"
    _to_approve_state = "in_progress"
    _approved_state = "confirmed"
    _rejected_state = "rejected"
    _subject_prefix = "[Download Documents]"
    _subject_code = "name"
    _enable_restart_validation = False
    # _rec_name = "completed_name"

    _tier_validation_manual_config = False

    name = fields.Char(string='Name')
    date_request = fields.Date(string='Date Request', default=lambda self: fields.Date.today())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled')
    ], string='State', default='draft', tracking=True)
    code_system = fields.Char("Code", readonly=True)
    issuing_authority = fields.Many2one('res.company', string='Issuing Authority')
    document_type = fields.Many2one('document.category', string='Document Type')
    document_code = fields.Char(string='Document Code', required=True)
    version = fields.Char(string='Version', default='V01')
    release_date = fields.Date(string='Release Date')
    expiration_date = fields.Date(string='Expiration Date')
    reason_request = fields.Text(string='Reason Request')
    tag_ids = fields.Many2many('documents.tag', string="Tags")
    is_emergency = fields.Boolean(string='Emergency')
    last_edit_date = fields.Date(string='Last Edit Date')
    user_request_id = fields.Many2one('res.users', string='Owner')
    document_id = fields.Many2one('documents.document', string='Document Detail')
    request_approve = fields.Boolean(related='document_id.request_approve', string='Request Download')
    is_request_validation = fields.Boolean(string='Is Request Validation', compute='_compute_request_validation')
    tier_definition_ids = fields.One2many('tier.definition', 'download_id', string='Tier Definition')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code_system'] = self.env['ir.sequence'].next_by_code('sequence.download.document')
        res = super(DownloadDocuments, self).create(vals_list)
        if res.tier_definition_ids:
            for rec in res.tier_definition_ids:
                rec.definition_domain = [('id', '=', res.id)]
        return res

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You cannot delete download that are not in draft state"))
            record.tier_definition_ids.unlink()
        return super(DownloadDocuments, self).unlink()

    def action_download(self):
        self.document_id.ensure_one()
        action = {
            'type': "ir.actions.act_url",
            'target': "new",
        }
        if self.document_id.type == 'binary':
            action['url'] = '/documents/content/%s' % self.document_id.id
        return action

    def reject_tier(self):
        documents_document = self.env['documents.document'].browse(self.document_id.id)
        if documents_document:
            documents_document.write({
                'is_download': False
            })
        return super(DownloadDocuments, self).reject_tier()

    def _compute_request_validation(self):
        for rec in self:
            uid = self.env.user.id
            if uid == rec.create_uid.id:
                rec.is_request_validation = True
            else:
                rec.is_request_validation = False
