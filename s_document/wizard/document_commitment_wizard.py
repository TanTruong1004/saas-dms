from odoo import models, fields, api
from odoo.exceptions import UserError


class DocumentCommitmentWizard(models.Model):
    _name = 'document.commitment.wizard'

    document_id = fields.Many2one('documents.document', string="Document")
    commitment = fields.Text(string='Commitment')
    feedback = fields.Text(string='Feedback')
    is_commited = fields.Selection([('0', 'I read and commited')], string='You must check the commitment checkbox to confirm.')
    def action_confirm(self):
        pass
