# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
from datetime import timedelta, datetime
import re


class DocumentsDocument(models.Model):
    _name = "documents.document"
    _inherit = ["documents.document", "tier.validation"]

    _state_field = "state"
    _state_from = ["draft", "in_progress"]
    _state_to = ["confirmed"]
    _cancel_state = "canceled"
    _to_approve_state = "in_progress"
    _approved_state = "confirmed"
    _rejected_state = "rejected"
    _subject_prefix = "[Document Management System]"
    _subject_code = "name"
    _enable_restart_validation = False
    _rec_name = "name"

    _tier_validation_manual_config = False

    def _get_requested_notification_subtype(self):
        return "s_document.documents_document_tier_validation_requested"

    def _get_accepted_notification_subtype(self):
        return "s_document.documents_document_tier_validation_accepted"

    def _get_rejected_notification_subtype(self):
        return "s_document.documents_document_tier_validation_rejected"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('confirmed', 'Confirmed'),
        ('done', 'Published'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled')
    ], string='State', default='draft', tracking=True)

    code_system = fields.Char("Code", readonly=True)
    completed_name = fields.Text(string='Document Name', compute='_compute_completed_name', store=True)
    issuing_authority = fields.Many2one('res.company', string='Issuing Authority')
    document_type = fields.Many2one('document.category', string='Document Category', required=True)
    document_code = fields.Char(string='Document Code', required=True, copy=False)
    version = fields.Char(string='Version', required=True, default='V', copy=False)
    release_date = fields.Date(string='Release Date')
    expiration_date = fields.Date(string='Expiration Date')
    document_description = fields.Text(string='Document Description')
    request_reason = fields.Text(string='Request Reason')
    request_approve = fields.Boolean(string='Request Download', default=False)
    is_commited = fields.Boolean(string='Commited', compute='_compute_is_commited')
    commitment_count = fields.Integer(compute='compute_commitment_count')
    is_download = fields.Boolean(string='Downloaded', compute='_compute_is_download')
    download_count = fields.Integer(compute='compute_download_count')
    is_emergency = fields.Boolean(string='Emergency')
    commitment_required = fields.Boolean(string='Request Commit', default=False)
    tier_definition_ids = fields.One2many('tier.definition', 'document_id', string='Tier Definition')
    name = fields.Char('Detail name document')
    custom_update_date = fields.Date('Last Edited')
    view_counts = fields.Char(string='View Counts')
    unique_view_count = fields.Integer(string='Unique View Count', compute='_compute_unique_view_count')
    custome_name_file = fields.Char()
    is_expiration = fields.Boolean(string='Expiration Config', compute='_expiration_config', search='_search_is_expiration')

    def _search_is_expiration(self, operator, value):
        remaining_days = int(self.env['ir.config_parameter'].sudo().get_param('s_document.remaining_days', 10))
        expiration_date_check = datetime.now() + timedelta(days=remaining_days)

        invalid_ids = self.search(domain=([('expiration_date', '<=', expiration_date_check),('expiration_date', '>=', datetime.now().date())])).ids
        return [('id', 'in', invalid_ids)]

    def _expiration_config(self):
        remaining_days = int(self.env['ir.config_parameter'].sudo().get_param('s_document.remaining_days', 10))
        expiration_date_check = datetime.now() + timedelta(days=remaining_days)
        for rec in self:
            rec.is_expiration = True if expiration_date_check == self.expiration_date else False


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code_system'] = self.env['ir.sequence'].next_by_code('sequence.document')
        res = super(DocumentsDocument, self).create(vals_list)
        for record in res:
            if record.attachment_id.index_content == 'image' and record.res_model == 'documents.document':
                record.attachment_id.write({
                    'res_field': 'thumbnail',
                    'res_model': 'documents.document',
                    'res_id': record.id,
                })
        return res


    # Method to compute the completed_name field
    @api.depends('name')
    def _compute_completed_name(self):
        for record in self:
            record.completed_name = record.name if record.name else ''

    @api.onchange('datas')
    def _change_element_document_name(self):
        if self.custome_name_file:
            self.name = self.custome_name_file
    @api.onchange('issuing_authority')
    def _change_element_workspace(self):
        self.folder_id = False

    def _compute_unique_view_count(self):
        for record in self:
            if not record.view_counts:
                record.unique_view_count = 0
            else:
                record.unique_view_count = len(list(record.view_counts.split(',')))

    @api.onchange('folder_id')
    def change_element_tags(self):
        self.tag_ids = False

    @api.onchange('custom_update_date')
    def change_release_date_by_edited_date(self):
        self.release_date = self.custom_update_date

    @api.onchange('tier_definition_ids')
    def onchange_tier_definition(self):
        if self.tier_definition_ids:
            for rec in self.tier_definition_ids:
                tier_definition = self.env['ir.model'].search([('model', '=', 'documents.document')], limit=1)
                rec.model_id = tier_definition.id if tier_definition else False
                rec.definition_domain = [('id', '=', self._origin.id)]
                rec.notify_on_accepted = True
                rec.notify_on_create = True
                rec.notify_on_rejected = True
                rec.notify_on_restarted = True
                rec.notify_status_on_action = True
                rec.has_comment = True

    @api.onchange('document_type')
    def _check_document_type(self):
        self.document_code = self.document_type.code

    @api.constrains('tier_definition_ids')
    def check_tier_definition(self):
        for line in self.tier_definition_ids:
            check_reviewer = self.tier_definition_ids.filtered(lambda x: x.reviewer_id == line.reviewer_id)
            if len(check_reviewer) > 1:
                raise UserError(
                    _("%s has already been defined in The Tier Definition.Please review!!", line.reviewer_id.name))
            check_approve_request = self.tier_definition_ids.filtered(lambda x: x.approve_request == True)
            if len(check_approve_request) > 1:
                raise UserError(
                    _("You are only allowed to check one option in the Approval Request step in The Tier Definition.Please review!!"))
            else:
                if len(check_approve_request) == 0:
                    raise UserError(
                        _("You need to check the Approve Request column in the  Approval Request step in The Tier Definition.Please review!!"))

    @api.constrains('document_code', 'version')
    def checkout_rule_code_version(self):
        for rec in self:
            if rec.document_code and rec.version:
                if not rec.document_type.code in rec.document_code or not rec.regex_number(rec.document_code):
                    raise UserError(_("The Document Category must include both letters and numbers"))
                elif not "V" in rec.version or not rec.regex_number(rec.version):
                    raise UserError(_("The version must include both letters and numbers"))
                else:
                    version_c = self.env["documents.document"].search(
                        [('version', '=', rec.version), ('document_code', '=', rec.document_code),
                         ('issuing_authority', '=', rec.issuing_authority.name), ('id', '!=', rec.id)],
                        limit=1)
                    if version_c:
                        raise UserError(_("Upload request for This document version and document code that already exists"))

    @api.constrains('expiration_date')
    def check_expiration_date(self):
        for rec in self:
            if rec.expiration_date:
                if datetime.now().date() > rec.expiration_date:
                    raise UserError(_("Expiration date must be greater than or equal to today's date"))
                if rec.issuing_authority:
                    if not rec.env.company == rec.issuing_authority:
                        raise UserError(_("Please select the SBU that matches the chosen company"))

    def write(self, vals):
        if self.tier_definition_ids:
            for rec in self.tier_definition_ids:
                tier_definition = self.env['ir.model'].search([('model', '=', 'documents.document')], limit=1)
                rec.model_id = tier_definition.id if tier_definition else False
                rec.definition_domain = [('id', '=', self._origin.id)]
                rec.notify_on_accepted = True
                rec.notify_on_create = True
                rec.notify_on_rejected = True
                rec.notify_on_restarted = True
                rec.notify_status_on_action = True
                rec.has_comment = True
        if 'thumbnail' in vals or 'thumbnail_status' in vals or 'view_counts' in vals:
            context = self._context.copy()
            context['skip_validation_check'] = True
            return super(DocumentsDocument, self.with_context(context)).write(vals)
        return super(DocumentsDocument, self).write(vals)

    def _compute_is_commited(self):
        for record in self:
            commitment = self.env['document.commitment.wizard'].search([
                ('document_id', '=', record.id),
                ('create_uid', '=', self.env.user.id)
            ])
            record.is_commited = bool(commitment)

    def check_is_able_to_download(self, list_user):
        uid = self.env.user.id
        if uid in list_user:
            return True

    def _compute_user_download(self):
        for rec in self:
            list_user = set()
            download_documents = self.env['download.documents'].search(
                [('document_id', '=', rec.id), ('state', '=', 'confirmed')])
            if download_documents:
                for download in download_documents:
                    list_user.add(download.create_uid.id)
            if rec.review_ids:
                for review in rec.review_ids:
                    if review.reviewer_ids:
                        for reviewer in review.reviewer_ids:
                            list_user.add(reviewer.id)
                    if review.reviewer_group_id:
                        for user in review.reviewer_group_id.users:
                            list_user.add(user.id)
            if rec.global_permission:
                res_users = self.env['res.users'].sudo().search([])
                list_user.update(user.id for user in res_users)
            elif rec.document_share_access_ids:
                for line in rec.document_share_access_ids:
                    if any(permission.code == 'download' for permission in line.onlyoffice_permission_ids):
                        list_user.add(line.user_id.id)
            if self.env.user.has_group(
                    'base.group_system') or self.env.user.partner_id in rec.message_follower_ids.partner_id:
                list_user.add(self.env.user.id)
            list_user.add(rec.create_uid.id)
            list_user.add(rec.owner_id.id)
            rec.is_user_download = list(list_user)
            rec.is_downloadable = self.check_is_able_to_download(list_user)

    def _compute_is_download(self):
        for record in self:
            download_documents = self.env['download.documents'].search([
                ('document_id', '=', record.id),
                ('create_uid', '=', self.env.user.id),
                ('state', 'not in', ('rejected', 'canceled'))
            ])
            if download_documents:
                record.is_download = bool(download_documents)
            else:
                record.is_download = False

    def compute_commitment_count(self):
        for record in self:
            record.commitment_count = self.env['document.commitment.wizard'].search_count(
                [('document_id', '=', record.id)])

    def compute_download_count(self):
        for record in self:
            record.download_count = self.env['download.documents'].search_count(
                ['|', '&', ('document_id', '=', record.id), ('request_approve', '=', False), '&',
                 ('document_id', '=', record.id), ('state', '=', 'confirmed')])

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
            # Add suffix to the document name to indicate it's a copy
        if not default.get('name'):
            default['name'] = _("%s (copy)") % (self.name)
            # Create a copy of the document without changing the version
        return super(DocumentsDocument, self).copy(default)

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You cannot delete documents that are not in draft state."))
            record.tier_definition_ids.unlink()
        return super(DocumentsDocument, self).unlink()

    def action_request_download(self):
        view_id = self.env.ref('s_document.view_download_documents').id
        model_id = self.env['ir.model'].search([('model', '=', 'download.documents')], limit=1)
        tier_definition = self.tier_definition_ids.filtered(lambda c: c.approve_request == True)
        tier_definition_ids = [(0, 0, {
            'name': tier_definition.name,
            'model_id': model_id.id if model_id else False,
            'reviewer_id': tier_definition.reviewer_id.id,
            'approve_request': tier_definition.approve_request,
            'notify_reminder_delay': tier_definition.notify_reminder_delay,
            'notify_on_accepted': True,
            'notify_on_create': True,
            'notify_on_rejected': True,
            'notify_on_restarted': True,
            'notify_status_on_action': True,
            'has_comment': True,
        })]

        ctx = dict(default_document_id=self.id,
                   default_user_request_id=self.owner_id.id,
                   default_issuing_authority=self.issuing_authority.id,
                   default_document_type=self.document_type.id,
                   default_version=self.version,
                   default_document_code=self.document_code,
                   default_release_date=self.release_date,
                   default_expiration_date=self.expiration_date,
                   default_tag_ids=self.tag_ids.ids,
                   default_last_edit_date=self.write_date,
                   default_tier_definition_ids=tier_definition_ids if self.request_approve else False
                   )
        action = {
            'type': "ir.actions.act_window",
            'res_model': 'download.documents',
            'name': _(f'Request Download Document'),
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[view_id, 'form']],
            'view_id': view_id,
            'target': 'current',
            'context': ctx
        }
        return action

    def action_open_document_form(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Document Form',
            'view_mode': 'form',
            'view_id': self.env.ref('s_document.view_sdocument_document_view_new_form').id,
            'res_model': 'documents.document',
            'res_id': self.id,
            'target': 'current',
            'id': self.env.ref('documents.document_action').id
        }
        return action

    def action_open_release_wizard(self):

        return {
            'type': 'ir.actions.act_window',
            'name': (_('Document Release')),
            'view_mode': 'form',
            'res_model': 'document.release.wizard',
            'target': 'new',
            'context': {
                'default_folder_id': self.folder_id.id,
                'default_expiration_date': self.expiration_date,
                'active_ids': self.ids,
            },
        }

    def action_open_commit_wizard(self):
        ctx = dict(default_document_id=self.id)
        return {
            'type': 'ir.actions.act_window',
            'name': (_('Would you like to commit?')),
            'view_mode': 'form',
            'res_model': 'document.commitment.wizard',
            'target': 'new',
            'context': ctx
        }

    @api.model
    def create_documents_document_form(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Create Document',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(self.env.ref('s_document.view_sdocument_document_view_new_form').id, 'form')],
            'target': 'current',
            'id': self.env.ref('documents.document_action').id
        }
        return action

    def detail_documents_document_form(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Create Document',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id' : self.id,
            'views': [(self.env.ref('s_document.view_sdocument_document_view_new_form').id, 'form')],
            'target': 'current',
            'id': self.env.ref('documents.document_action').id
        }
        return action

    def action_list_download(self):
        for rec in self:
            domain = [('document_id', '=', rec.id)]
            return {
                'name': _('Download Document'),
                'type': 'ir.actions.act_window',
                'res_model': 'download.documents',
                'view_mode': 'tree,form',
                'domain': domain,
                'context': "{'create':False,'edit':False}"
            }

    def get_commitment_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': (_('Commitments')),
            'view_mode': 'tree',
            'res_model': 'document.commitment.wizard',
            'domain': [('document_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def check_expiration_dates(self):
        remaining_days = int(self.env['ir.config_parameter'].sudo().get_param('s_document.remaining_days', 10))
        expiration_date_check = datetime.now() + timedelta(days=remaining_days)
        documents_to_notify = self.search([
            ('expiration_date', '=', expiration_date_check),
            ('state', '=', 'done')
        ])
        documents_expried = self.search([
            ('expiration_date', '<', datetime.now().date()),
            ('state', '!=', "in_progress"),
        ])
        if documents_expried:
            for record in documents_expried:
                record.write({'active': False})
        if documents_to_notify:
            for document in documents_to_notify:
                existing_activity = self.env['mail.activity'].search([
                    ('res_id', '=', document.id),
                    ('res_model', '=', 'documents.document'),
                    ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
                    ('user_id', '=', document.owner_id.id),
                ], limit=1)

                if not existing_activity:
                        list_user = {document.owner_id.id, document.create_uid.id}
                        for user in set(list_user):
                            document.activity_schedule(
                                'mail.mail_activity_data_todo',
                                user_id=user,
                                date_deadline = document.expiration_date,
                                note=_('The document "%s" will expire in %s days.') % (document.name, remaining_days)
                            )

    def increment_view_count(self):
        current_user = self.env.user
        id_users = self.view_counts.split(',') if self.view_counts else None
        if not self.view_counts:
            self.write({'view_counts': str(current_user.id)})
        else:
            if not str(self.env.uid) in id_users:
                self.write({'view_counts': str(current_user.id) + "," + self.view_counts})

    def regex_number(self, string):
        return bool(re.search(r"\d", string))

    def check_view(self):
        return (self.env.ref('base_tier_validation_report.tier_review_report_tree').id)

    def get_param_config_remind_date(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('s_document.remaining_days'))

    @api.autovacuum
    def _gc_clear_bin(self):
        pass

    def toggle_lock(self):
        self.ensure_one()
        current_user = self.env.user

        if self.lock_uid:
            if current_user == self.lock_uid or current_user.has_group(
                    'base.group_system') or self.create_uid == current_user:
                self.lock_uid = False
            else:
                raise UserError(_("You do not have the permissions to unlock this document."))
        else:
            if current_user.has_group('base.group_system') or self.create_uid == current_user:
                self.lock_uid = current_user.id
            else:
                raise UserError(_("You do not have the permissions to lock this document."))
