# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import re
from random import randint


class DocumentCategory(models.Model):
    _name = 'document.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Document Category'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            document_category = self.env['document.category'].search([
                ('code', '=', record.code),
                ('id', '!=', record.id)
            ])
            if document_category:
                raise UserError(_("Code already exists. Please review!!"))

    @api.onchange('code')
    def _onchange_code(self):
        if self.code:
            self.code = self.code.upper()
