from odoo import models, fields, api

class OnlyofficePermission(models.Model):
    _name = 'onlyoffice.permission'
    _description = 'Onlyoffice Permission'
    _rec_name = 'name'

    name = fields.Char(string='Permission Name', required=True)
    code = fields.Char(string='Permission Code', required=True)
    description = fields.Text(string='Description', required=True)
