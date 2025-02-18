# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import re
from random import randint


class DocumentFolder(models.Model):
    _inherit = 'documents.folder'

    is_approve = fields.Boolean(string="Is Approve", default=False)

    @api.model
    def write(self, vals):
        if 'is_approve' in vals:
            self._set_approved_for_all_children(vals.get('is_approve'))
        return super(DocumentFolder, self).write(vals)

    def _set_approved_for_all_children(self, approved_value):
        for child in self.children_folder_ids:
            child.write({'is_approve': approved_value})
            if child.children_folder_ids:
                child._set_approved_for_all_children(approved_value)

    def action_archive(self):
        if not self:
            return
        if self.document_ids:
            raise UserError(_("You cannot delete a folder that has linked documents."))
        elif self.children_folder_ids:
            raise UserError(_("You cannot delete a folder that has linked folder."))
        return super(DocumentFolder, self).unlink()

    def action_see_documents(self):
        domain = [('folder_id', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('s_document.view_document_tree_new').id, 'list'), (self.env.ref('s_document.view_sdocument_document_view_new_form').id, 'form')],
            'view_mode': 'tree,form',
            'context': {'searchpanel_default_folder_id': self.id}
        }

    def check_is_approve(self):
        if self.is_approve:
            return True
        else:
            return False
