import requests

from requests.auth import HTTPBasicAuth

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class DropBoxCredentials(models.Model):
    _name = 'dropbox.credentials'
    _description = 'Dropbox Credentials'

    name = fields.Char(string="Account Name")
    access_token = fields.Char(string="Access Token")
    folder_path = fields.Char(string="Folder Path")
    current_account = fields.Boolean(string="Active?", default=False)
    link_url = fields.Char(string="Link Url")
    dropbox_data_limit_mb = fields.Integer(string="Data Limit (MB)", default=20)
    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Client Secret")
    refresh_token = fields.Char(string="Refresh Token")
    expires_at = fields.Float(string="Expires At")
    authorization_code = fields.Char(string="Authorization Code")

    @api.model
    def create(self, vals):
        if vals["current_account"]:
            self.env[self._name].search([]).write({"current_account": False})
        return super(DropBoxCredentials, self).create(vals)

    def write(self, vals):
        if "current_account" in vals and vals["current_account"]:
            self.env[self._name].search([]).write({"current_account": False})
        return super(DropBoxCredentials, self).write(vals)

    def get_dropbox_credentials(self):
        def_credential = self.env[self._name].search([('current_account', '=', True)])
        return def_credential[0] if len(def_credential) > 0 else None

    def refresh_access_token(self):
        try:
            dropbox_credentials = self.env['dropbox.credentials'].search([('current_account', '=', True)], limit=1)

            url = 'https://api.dropboxapi.com/oauth2/token'
            if dropbox_credentials.refresh_token and dropbox_credentials:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": dropbox_credentials.refresh_token,
                    "client_id": dropbox_credentials.client_id,
                    "client_secret": dropbox_credentials.client_secret
                }

                response = requests.post(url, data=data)
                new_token_data = response.json()
                dropbox_credentials.write({
                    'access_token': new_token_data.get('access_token'),
                    'expires_at': new_token_data.get('expires_in') / 3600
                })
            else:
                raise UserError(_(f"Dropbox account information not found"))
        except requests.exceptions.RequestException as e:
            _logger.error(f"Lỗi khi gọi API Dropbox: {e}")
            raise UserError(_(f"Error calling Dropbox API: {e}"))
        except Exception as e:
            _logger.error(f"Lỗi không xác định: {e}")
            raise UserError(_(f"Unknown error: {e}"))

    def action_check_code_dropbox(self):
        try:
            dropbox_credentials = self.env['dropbox.credentials'].search([('current_account', '=', True)], limit=1)
            if dropbox_credentials:
                dropbox_credentials.write({'refresh_token': '', 'expires_at': 0})
                authorize_url = f"https://www.dropbox.com/oauth2/authorize?client_id={dropbox_credentials.client_id}&token_access_type=offline&response_type=code"
                return {
                    'type': 'ir.actions.act_url',
                    'url': authorize_url,
                    'target': 'new',
                }
            else:
                raise UserError(_(f"Dropbox account information not found"))
        except Exception as e:
            _logger.error(f"Lỗi khi tạo URL xác thực Dropbox: {e}")
            raise UserError(_(f"Error generating Dropbox authentication URL: {e}"))

    def action_refresh_code_dropbox(self):
        try:
            dropbox_credentials = self.env['dropbox.credentials'].search([('current_account', '=', True)], limit=1)
            url = 'https://api.dropboxapi.com/oauth2/token'
            if dropbox_credentials and dropbox_credentials.authorization_code:
                data = {
                    'code': dropbox_credentials.authorization_code,
                    'grant_type': 'authorization_code'
                }

                response = requests.post(url, data=data, auth=HTTPBasicAuth(dropbox_credentials.client_id,
                                                                            dropbox_credentials.client_secret))
                if response.status_code == 200:
                    data = response.json()
                    dropbox_credentials.write({
                        'access_token': data.get('access_token'),
                        'refresh_token': data.get('refresh_token'),
                        'expires_at': data.get('expires_in') / 3600,
                    })
                else:
                    _logger.error(response)
                    raise UserError(_(f"Request failed with status code {response.status_code}"))
            else:
                raise UserError(_(f"Dropbox account information not found"))
        except requests.exceptions.RequestException as e:
            _logger.error(f"Lỗi khi gọi API Dropbox: {e}")
            raise UserError(_(f"Error calling Dropbox API: {e}"))
        except Exception as e:
            _logger.error(f"Lỗi không xác định: {e}")
            raise UserError(_(f"Unknown error: {e}"))

