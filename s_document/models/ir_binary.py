import logging
import werkzeug.http
from datetime import datetime
from mimetypes import guess_extension

from odoo import models
from odoo.exceptions import MissingError, UserError
from odoo.http import Stream, request
from odoo.tools import file_open, replace_exceptions
from odoo.tools.image import image_process, image_guess_size_from_field_name
from odoo.tools.mimetypes import guess_mimetype, get_extension
from . import documents_document

class IrBinary(models.AbstractModel):
    _inherit = 'ir.binary'

    def _get_stream_from(
            self, record, field_name='raw', filename=None, filename_field='name',
            mimetype=None, default_mimetype='application/octet-stream', ):
        if isinstance(record, documents_document.DocumentsDocument):
            with replace_exceptions(ValueError, by=UserError(f'Expected singleton: {record}')):
                record.ensure_one()

            try:
                field_def = record._fields[field_name]
            except KeyError:
                raise UserError(f"Record has no field {field_name!r}.")
            if field_def.type != 'binary':
                raise UserError(
                    f"Field {field_def!r} is type {field_def.type!r} but "
                    f"it is only possible to stream Binary or Image fields."
                )

            stream = self._record_to_stream(record, field_name)

            if stream.type in ('data', 'path'):
                if mimetype:
                    stream.mimetype = mimetype
                elif not stream.mimetype:
                    if stream.type == 'data':
                        head = stream.data[:1024]
                    else:
                        with open(stream.path, 'rb') as file:
                            head = file.read(1024)
                    stream.mimetype = guess_mimetype(head, default=default_mimetype)

                if record["custome_name_file"]:
                    stream.download_name = record['completed_name'] + record["custome_name_file"][record['custome_name_file'].rfind('.'):]
                else:
                    stream.download_name = record['name']

                stream.download_name = stream.download_name.replace('\n', '_').replace('\r', '_')
                if (not get_extension(stream.download_name)
                        and stream.mimetype != 'application/octet-stream'):
                    stream.download_name += guess_extension(stream.mimetype) or ''
            return stream
        else:
            return super(IrBinary, self)._get_stream_from(record, field_name, filename,
                                                          filename_field,
                                                          mimetype, default_mimetype, )
