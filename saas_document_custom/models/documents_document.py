# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os

import dropbox
import requests
import pytz
import uuid

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta, datetime

import tempfile
import base64
import logging

_logger = logging.getLogger(__name__)


class DocumentsDocument(models.Model):
    _inherit = ["documents.document"]

    def _compute_user_download(self):
        for rec in self:
            list_user = set()
            download_documents = self.env['download.documents'].search(
                [('document_id', '=', rec.id), ('state', '=', 'confirmed')])
            if download_documents:
                for download in download_documents:
                    list_user.add(download.create_uid.id)
            if rec.review_ids:
                for review in rec.review_ids:
                    if review.reviewer_ids:
                        for reviewer in review.reviewer_ids:
                            list_user.add(reviewer.id)
                    if review.reviewer_group_id:
                        for user in review.reviewer_group_id.users:
                            list_user.add(user.id)
            if rec.global_permission:
                res_users = self.env['res.users'].sudo().search([])
                list_user.update(user.id for user in res_users)
            elif rec.document_share_access_ids:
                for line in rec.document_share_access_ids:
                    if any(permission.code == 'download' for permission in line.onlyoffice_permission_ids):
                        list_user.add(line.user_id.id)
            if self.env.user.has_group(
                    'base.group_system') or self.env.user.partner_id in rec.message_follower_ids.partner_id:
                list_user.add(self.env.user.id)
            list_user.add(rec.create_uid.id)
            list_user.add(rec.owner_id.id)
            rec.is_user_download = list(list_user)
            rec.is_downloadable = self.check_is_able_to_download(list_user)
