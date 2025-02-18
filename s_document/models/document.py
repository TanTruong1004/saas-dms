# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
from datetime import timedelta, datetime
from odoo.addons.documents.models.documents_document import Document
import re


def write(self, vals):
    if vals.get('folder_id') and not self.env.is_superuser():
        folder = self.env['documents.folder'].browse(vals.get('folder_id'))
        if not folder.has_write_access:
            raise AccessError(_("Bạn không có quyền di chuyển tài liệu vào không gian làm việc đó."))

    attachment_id = vals.get('attachment_id')
    if attachment_id:
        self.ensure_one()
    for record in self:

        if record.type == 'empty' and ('datas' in vals or 'url' in vals):
            body = _("Tài liệu yêu cầu: %s tải lên bởi: %s", record.name, self.env.user.name)
            record.with_context(no_document=True).message_post(body=body)

        if record.attachment_id:
            # versioning
            if attachment_id:
                if attachment_id in record.previous_attachment_ids.ids:
                    record.previous_attachment_ids = [(3, attachment_id, False)]
                record.previous_attachment_ids = [(4, record.attachment_id.id, False)]
            if 'datas' in vals:
                old_attachment = record.attachment_id.with_context(no_document=True).copy()
                # removes the link between the old attachment and the record.
                old_attachment.write({
                    'res_model': 'documents.document',
                    'res_id': record.id,
                })
                record.previous_attachment_ids = [(4, old_attachment.id, False)]
        elif vals.get('datas') and not vals.get('attachment_id'):
            res_model = vals.get('res_model', record.res_model or 'documents.document')
            res_id = vals.get('res_id') if vals.get('res_model') else record.res_id if record.res_model else record.id
            if res_model and res_model != 'documents.document' and not self.env[res_model].browse(res_id).exists():
                record.res_model = res_model = 'documents.document'
                record.res_id = res_id = record.id
            attachment = self.env['ir.attachment'].with_context(no_document=True).create({
                'name': vals.get('name', record.name),
                'res_model': res_model,
                'res_id': res_id
            })
            record.attachment_id = attachment.id
            record.with_context(no_document=True)._process_activities(attachment.id)

    # pops the datas and/or the mimetype key(s) to explicitly write them in batch on the ir.attachment
    # so the mimetype is properly set. The reason was because the related keys are not written in batch
    # and because mimetype is readonly on `ir.attachment` (which prevents writing through the related).
    attachment_dict = {key: vals.pop(key) for key in ['datas', 'mimetype'] if key in vals}

    write_result = super(Document, self).write(vals)
    if attachment_dict:
        self.mapped('attachment_id').write(attachment_dict)

    if 'attachment_id' in vals:
        self.attachment_id.check('read')

    return write_result

Document.write = write
