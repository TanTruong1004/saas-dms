# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os

import dropbox
import requests
import pytz
import uuid

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta, datetime

import tempfile
import base64
import logging

_logger = logging.getLogger(__name__)


class DocumentsDocument(models.Model):
    _name = "documents.document"
    _inherit = ["documents.document"]

    file_content = fields.Text(string='File Content')
    dbx_link = fields.Char(string="Dropbox Link")
    document_share_access_ids = fields.One2many('documents.share.access', 'document_id', string="Document Share Access")
    link_url = fields.Char(string="Link Url")
    uuid = fields.Char(string="UUID")
    global_permission = fields.Boolean(string="Global Permission")
    error_description_read = fields.Char(string='Error Description Read')
    error_description_push = fields.Char(string='Error Description Push')
    is_downloadable = fields.Boolean(string='Able To Download', compute='_compute_user_download')
    is_user_download = fields.Char(string='User Download', compute='_compute_user_download')
    onlyoffice_permission_ids = fields.Many2many('onlyoffice.permission', string="Permission")
    state_read = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], default='pending', string="State Read", tracking=True)
    state_push = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], default='pending', string="State Push", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(DocumentsDocument, self).create(vals_list)
        for record, vals in zip(res, vals_list):
            if record.datas:
                record.check_dropbox_file_content(record, record.datas, record.name)
        return res

    def _compute_unique_view_count(self):
        for record in self:
            if not record.view_counts:
                record.unique_view_count = 0
            else:
                record.unique_view_count = len(list(record.view_counts.split(',')))

    def check_is_able_to_download(self, list_user):
        uid = self.env.user.id
        if uid in list_user:
            return True

    def _compute_user_download(self):
        for rec in self:
            list_user = set()
            if rec.global_permission:
                res_users = self.env['res.users'].sudo().search([])
                list_user.update(user.id for user in res_users)
            elif rec.document_share_access_ids:
                for line in rec.document_share_access_ids:
                    if any(permission.code == 'download' for permission in line.onlyoffice_permission_ids):
                        list_user.add(line.user_id.id)
            if self.env.user.has_group('base.group_system'):
                list_user.add(self.env.user.id)
            list_user.add(rec.create_uid.id)
            list_user.add(rec.owner_id.id)
            rec.is_user_download = list(list_user)
            rec.is_downloadable = self.check_is_able_to_download(list_user)

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

    @api.constrains('document_share_access_ids')
    def check_document_share_access(self):
        for line in self.document_share_access_ids:
            check_user = self.document_share_access_ids.filtered(lambda x: x.user_id == line.user_id)
            if len(check_user) > 1:
                raise UserError(_("%s selected. Please review!!", line.user_id.name))

    @api.onchange('global_permission')
    def _onchange_global_permission(self):
        for rec in self:
            if rec.global_permission:
                if rec.document_share_access_ids:
                    rec.document_share_access_ids = [(5, 0, 0)]

    def write(self, vals):
        for rec in self:
            if vals.get('global_permission') and rec.document_share_access_ids:
                rec.document_share_access_ids.unlink()
            if 'datas' in vals and vals.get('datas') and vals.get('name'):
                rec.check_dropbox_file_content(rec, vals.get('datas'), vals.get('name'))
        return super(DocumentsDocument, self).write(vals)

    def check_dropbox_file_content(self, record=None, data=None, name=None):
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        current_time = datetime.now(timezone)
        parameter = self.env['ir.config_parameter'].sudo()
        parameter_ip_address = parameter.get_param('saas_documents.doc_url')
        parameter_is_file_content = parameter.get_param('saas_documents.is_file_content')
        parameter_is_upload_dropbox = parameter.get_param('saas_documents.is_upload_dropbox')
        if parameter_ip_address and parameter_is_file_content:
            record._extract_file_content(parameter_ip_address, data, name)
        file_size = len(data) * 3 // 4
        try:
            dropbox_credentials = self.env['dropbox.credentials'].sudo().search([('current_account', '=', True)],
                                                                                limit=1)
            if dropbox_credentials and parameter_is_upload_dropbox:
                file_size_limit = dropbox_credentials.dropbox_data_limit_mb * 1024 * 1024
                if file_size > file_size_limit:
                    record.state_push = 'in_progress'
                    file_name = name
                    path = f'/{current_time.strftime("%Y%m%d_%H%M%S")}_{file_name}'
                    data = record.with_delay(channel='channel_upload').upload_to_dropbox(record, path,
                                                                                         dropbox_credentials.access_token)
                else:
                    self.dbx_link = False
        except Exception as e:
            raise UserError(f"Lỗi khi tải tệp lên Dropbox: {str(e)}")

    def _extract_file_content(self, parameter_ip_address, datas, name):
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        current_time = datetime.now(timezone)
        file_extension = os.path.splitext(name)[1].lower()
        type_file = ''
        if file_extension in ['.doc', '.docx']:
            type_file = 'word'
        elif file_extension in ['.xls', '.xlsx']:
            type_file = 'excel'
        elif file_extension == '.pdf':
            type_file = 'pdf'
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            type_file = 'image'
        elif file_extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            type_file = 'audio'
        if type_file:
            decoded_data = base64.b64decode(datas)
            temp_dir = tempfile.gettempdir()
            name_format = f'{current_time.strftime("%Y%m%d_%H%M%S")}_{name}'
            path = f'{temp_dir}/{name_format}'
            with open(path, 'wb') as file:
                file.write(decoded_data)
            _logger.info(f'{temp_dir}, {path}')
            data = self.with_delay(channel='channel_extract').call_file_content_api(parameter_ip_address, type_file,
                                                                                    path)
        self.state_read = 'in_progress'

    def open_user_access_popup(self):
        uuid_data = str(uuid.uuid4())
        link_url = f'{self.get_base_url()}/web/document/shared/{uuid_data}'
        if not self.uuid and not self.link_url:
            self.write({'link_url': link_url,
                        'uuid': uuid_data})
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Share Document'),
            'res_model': 'documents.document',
            'view_mode': 'form',
            'views': [(self.env.ref('documents.document_view_form').id, 'form')],
            'target': 'new',
            'res_id': self.id,

        }
        return action

    def download_file(self):
        if '&dl=' in self.dbx_link:
            download_link = self.dbx_link.replace('&dl=0', '&dl=1')
        else:
            download_link = self.dbx_link + '&dl=1'
        return {
            'url': download_link,
            'target': 'new',
        }

    def upload_to_dropbox(self, res, path, access_token):
        try:
            dbx = dropbox.Dropbox(f'{access_token}')
            file_data_encoded = base64.b64encode(res.datas).decode('utf-8')
            file_data = base64.b64decode(file_data_encoded)
            dropbox_id = dbx.files_upload(file_data, path, mute=True)
            shared_links = dbx.sharing_list_shared_links(path=path, direct_only=True)
            dropbox_link = shared_links.links[
                0].url if shared_links.links else dbx.sharing_create_shared_link_with_settings(path).url
            if res:
                if res.attachment_id:
                    res.attachment_id.datas = False
                res.write({
                    'datas': False,
                    'dbx_link': dropbox_link,
                    'state_push': 'done'
                })
        except Exception as e:
            if res:
                res.write({
                    'state_push': 'error',
                    'error_description_push': str(e)
                })
                self.env.cr.commit()
            raise ValidationError(_(f"Failed to get file content: {str(e)}"))

    def call_file_content_api(self, parameter_ip_address, file_extension, path):
        try:
            if not parameter_ip_address:
                raise UserError(_("IP address has not been configured yet. Please review!"))
            get_file_content_endpoint = f'{parameter_ip_address}/read_doc'
            body_data = {
                'path': path,
                'type': file_extension
            }
            response = requests.post(get_file_content_endpoint, json=body_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'Success':
                    self.write({
                        'file_content': data.get('text'),
                        'state_read': 'done'
                    })
                else:
                    self.write({
                        'state_read': 'error',
                        'error_description_read': data.get('text')
                    })
                    raise ValidationError(_(f"{data.get('text')}"))
            else:
                _logger.error(response)
                raise ValidationError(_(f"Request failed with status code {response.status_code}"))
        except Exception as e:
            self.write({
                'state_read': 'error',
                'error_description_read': str(e)
            })
            self.env.cr.commit()
            raise ValidationError(_(f"Failed to get file content: {str(e)}"))
