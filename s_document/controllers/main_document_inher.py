from odoo import http
from odoo.http import request
from odoo.addons.documents.controllers.documents import ShareRoute


class document_ShareRoute_inherit(ShareRoute):

    def _get_file_response_custome(self, res_id, share_id=None, share_token=None, field='raw'):
        """ returns the http response to download one file. """
        record = request.env['documents.document'].browse(int(res_id))

        if share_id:
            share = request.env['documents.share'].sudo().browse(int(share_id))
            record = share._get_documents_and_check_access(share_token, [int(res_id)], operation='read')
        if not record or not record.exists():
            raise request.not_found()

        if record.type == 'url':
            if isinstance(record.url, str):
                url = record.url if record.url.startswith(('http://', 'https://', 'ftp://')) else 'http://' + record.url
            else:
                url = record.url
            return request.redirect(url, code=307, local=False)
        return request.env['ir.binary']._get_stream_from(record, field).get_response(True)


    @http.route(['/documents/content/<int:id>'], type='http', auth='user')
    def documents_content(self, id):
        return self._get_file_response_custome(id)
