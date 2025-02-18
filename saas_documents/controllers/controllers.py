import json
import logging
import markupsafe
import re

from odoo import http
from odoo.http import request

from odoo.addons.onlyoffice_odoo.utils import file_utils
from odoo.addons.onlyoffice_odoo.utils import jwt_utils
from odoo.addons.onlyoffice_odoo.utils import config_utils

from odoo.addons.onlyoffice_odoo.controllers.controllers import Onlyoffice_Connector

from odoo.tools.translate import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
_mobile_regex = r"android|avantgo|playbook|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od|ad)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino"

dct={''}


class OnlyofficeConnectorInherit(Onlyoffice_Connector):

    @http.route("/web/document/shared/<string:slug>", auth="user", type="http", website=True)
    def share_document(self, slug, access_token=None):
        document = request.env["documents.document"].sudo().search([("uuid", "=", slug)], limit=1)
        attachment_id = document.attachment_id.id
        attachment = self.get_attachment(attachment_id)
        if not attachment:
            return request.not_found()

        attachment.validate_access(access_token)

        data = attachment.sudo().read(["id", "checksum", "public", "name", "access_token"])[0]
        filename = data["name"]

        can_read = attachment.check_access_rights("read", raise_exception=False) and file_utils.can_view(filename)
        can_write = attachment.check_access_rights("write", raise_exception=False) and file_utils.can_edit(filename)

        if (not can_read):
            raise Exception("cant read")

        return request.render("onlyoffice_odoo.onlyoffice_editor",
                              self.prepare_editor_values_1(attachment, access_token, slug, can_write))

    def prepare_editor_values_1(self, attachment, access_token, slug, can_write):
        data = attachment.read(["id", "checksum", "public", "name", "access_token"])[0]
        document_id = request.env["documents.document"].sudo().search([("uuid", "=", slug)], limit=1)
        additional_users_permissions = []
        data_permission = {'edit': False, 'review': False, 'comment': False, 'download': False, 'print': False}
        for document_share in document_id.document_share_access_ids:
            user_id = document_share.user_id.id
            user_name = document_share.user_id.name
            valid_permissions = {'edit', 'review', 'comment', 'download', 'print'}
            for permission in document_share.onlyoffice_permission_ids:
                if permission.code in valid_permissions:
                    data_permission[permission.code] = True
            additional_users_permissions.append({
                "id": user_id,
                "name": user_name,
                "permission": data_permission

            })
            if user_id == request.env.user.id:
                break
        if document_id.global_permission:
            for permission in document_id.onlyoffice_permission_ids:
                if permission.code in data_permission:
                    data_permission[permission.code] = True
            user_permission = data_permission
        else:
            has_permission = False
            user_permission = {}
            for user_perms in additional_users_permissions:
                if user_perms['id'] == request.env.user.id or document_id.create_uid.id == request.env.user.id:
                    has_permission = True
                    user_permission = user_perms.get('permission')
                    break
            if not has_permission:
                raise UserError(_("Bạn không có quyền truy cập tài liệu này. Vui lòng xem lại!!"))

        docserver_url = config_utils.get_doc_server_public_url(request.env)
        odoo_url = config_utils.get_base_or_odoo_url(request.env)
        filename = self.filter_xss(data["name"])

        security_token = jwt_utils.encode_payload(request.env, {"id": request.env.user.id},
                                                  config_utils.get_internal_jwt_secret(request.env))
        path_part = str(data["id"]) + "?oo_security_token=" + security_token + (
            "&access_token=" + access_token if access_token else "")

        document_type = file_utils.get_file_type(filename)
        is_mobile = bool(re.search(_mobile_regex, request.httprequest.headers.get("User-Agent"), re.IGNORECASE))

        root_config = {
            "width": "100%",
            "height": "100%",
            "type": "mobile" if is_mobile else "desktop",
            "documentType": document_type,
            "document": {
                "title": filename,
                "url": odoo_url + "onlyoffice/file/content/" + path_part,
                "fileType": file_utils.get_file_ext(filename),
                "key": str(data["id"]) + str(data["checksum"]),
                "permissions": user_permission,
            },
            "editorConfig": {
                "mode": "edit" if can_write and user_permission.get('edit') else "view",
                "lang": request.env.user.lang,
                "user": {"id": str(request.env.user.id), "name": request.env.user.name},
                "customization": {},
            },
        }

        if can_write:
            root_config["editorConfig"]["callbackUrl"] = odoo_url + "onlyoffice/editor/callback/" + path_part

        if jwt_utils.is_jwt_enabled(request.env):
            root_config["token"] = jwt_utils.encode_payload(request.env, root_config)

        return {"docTitle": filename,
                "docIcon": f"/onlyoffice_odoo/static/description/editor_icons/{document_type}.ico",
                "docApiJS": docserver_url + "web-apps/apps/api/documents/api.js",
                "editorConfig": markupsafe.Markup(json.dumps(root_config))}
