# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    doc_url = fields.Char(string='Doc Url', config_parameter='saas_documents.doc_url')
    is_file_content = fields.Boolean(string='Search File Content', config_parameter='saas_documents.is_file_content')
    is_upload_dropbox = fields.Boolean(string='Upload Dropbox', config_parameter='saas_documents.is_upload_dropbox')
