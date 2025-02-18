# -*- coding: utf-8 -*-

{
    'name': "Saas Document Custom",
    'author': "Snine",
    'company': 'Snine',
    'maintainer': 'Snine',
    'website': "https://www.snine.vn",
    'category': 'Productivity/Documents',
    'version': '17.0.1.0.0',
    'depends': ['base', 'documents', 's_document', 'saas_documents'],
    'data': [
        'security/ir.model.access.csv',
        'security/rule_document.xml',
        'views/document_document_view.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'post_init_hook': 'delete_document_rule',
    'uninstall_hook': 'setup_document_rule'
}
