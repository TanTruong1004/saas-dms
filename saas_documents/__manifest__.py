# -*- coding: utf-8 -*-

{
    'name': "Saas Documents",
    'summary': """Tích hợp thêm tìm kiếm nội dùng file và sử dụng Dropbox vào Documents.""",
    'author': "Snine",
    'company': 'Snine',
    'maintainer': 'Snine',
    'website': "https://www.snine.vn",
    'category': 'Productivity/Documents',
    'version': '17.0.1.0.0',
    'depends': ['base', 'documents', 'documents_spreadsheet'],
    'data': [
        'security/ir.model.access.csv',
        'security/rule_document.xml',
        'views/document_document_view.xml',
        'views/documents_workflow_rule_views.xml',
        'views/res_config_settings_views.xml',
        'views/credential_views.xml',
        'views/onlyoffice_permission_views.xml',
        'views/remove_odoo.xml',
        'views/document_create_views.xml',
        'views/menuitem.xml',

        'data/cron_dropbox.xml',
        'data/data_onlyoffice_permission.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'saas_documents/static/src/views/**/*.js',
            'saas_documents/static/src/views/**/*.xml',
            'saas_documents/static/src/css/custom_form_label.css',
        ]
    },
    'installable': True,
    'application': False,
}
