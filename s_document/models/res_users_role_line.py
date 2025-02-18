from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
import datetime
import pytz

class ResUsersRoleLine(models.Model):
    _inherit = 'res.users.role.line'

    @api.depends("date_from", "date_to")
    def _compute_is_enabled(self):
        tz_Vietnam = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        today = datetime.datetime.now(tz_Vietnam).date()
        for role_line in self:
            role_line.is_enabled = True
            if role_line.date_from:
                date_from = role_line.date_from
                if date_from > today:
                    role_line.is_enabled = False
            if role_line.date_to:
                date_to = role_line.date_to
                if today > date_to:
                    role_line.is_enabled = False
