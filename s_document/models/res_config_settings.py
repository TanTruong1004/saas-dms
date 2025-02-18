# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    remaining_days = fields.Integer(string='Remaning Days', default=10, config_parameter='s_document.remaining_days')
