from datetime import datetime
from odoo.exceptions import UserError
from odoo import models, fields, api,_

class DocumentReleaseWizard(models.TransientModel):
    _name = 'document.release.wizard'

    folder_id = fields.Many2one('documents.folder', string="Workspace")
    expiration_date = fields.Date(string="Expiration Date")

    @api.model
    def default_get(self, fields):
        defaults = super(DocumentReleaseWizard, self).default_get(fields)
        if 'default_folder_id' in self._context:
            defaults['folder_id'] = self._context.get('default_folder_id')
        if 'default_expiration_date' in self._context:
            defaults['expiration_date'] = self._context.get('default_expiration_date')
        return defaults

    def action_release_documents(self):
        active_ids = self.env.context.get('active_ids', [])
        documents = self.env['documents.document'].browse(active_ids)
        for doc in documents:
            doc.write({
                'state': 'done',
                'folder_id': self.folder_id.id,
                'expiration_date': self.expiration_date,
                'release_date': fields.Datetime.now(),
            })

    @api.constrains('expiration_date')
    def check_expiration_date(self):
        if self.expiration_date:
            if datetime.now().date() > self.expiration_date:
                raise UserError(_("Expiration date must be greater than or equal to today's date"))
