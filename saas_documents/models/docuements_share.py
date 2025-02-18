# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
from odoo.tools import consteq

from odoo.osv import expression

import uuid


class DocumentShare(models.Model):
    _inherit = 'documents.share'

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name or _("unnamed link")
