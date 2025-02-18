# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class DocumentsShareAccess(models.Model):
    _name = "documents.share.access"
    _description = 'Documents Share Access'

    user_id = fields.Many2one('res.users', string="User", required=True)
    onlyoffice_permission_ids = fields.Many2many('onlyoffice.permission', string="Permission")
    document_id = fields.Many2one('documents.document', string="Documents")
