# -*- coding: utf-8 -*-

{
    'name': "Sdocument",
    'summary': """Document management""",
    'description': """Document management""",
    'author': "Snine",
    'company': 'SNine',
    'maintainer': 'SNine',
    'website': "https://www.snine.vn",
    'category': 'Productivity/Documents',
    'version': '17.0.1.0.0',
    'depends': ['base', 'spreadsheet_dashboard', 'documents', 'documents_spreadsheet', 'base_tier_validation', 'tier_validation', 'documents_product', 'documents_hr', 'base_tier_validation_formula', 'base_tier_validation_forward', 'base_tier_validation_report', 'base_tier_validation_server_action'],
    'data': [
        'security/record_rule_document.xml',
        'security/ir.model.access.csv',
        'views/download_documents_view.xml',
        'views/document_document_view.xml',
        'views/document_category_view.xml',
        'views/documents_folder_view.xml',
        'views/documents_folder_view.xml',
        'views/inherit_tier_review_report_tree.xml',
        'views/inherit_tier_review_definition_form.xml',
        'views/inherit_document_setting_hide.xml',
        'views/my_document_view.xml',
        'views/tier_review_views.xml',
        'views/inherit_tag_view_form.xml',
        'views/res_config_settings_views.xml',
        'views/inherit_menu_configuration.xml',
        'views/menuitem.xml',

        'wizard/document_release_wizard_view.xml',
        'wizard/document_commitment_wizard_view.xml',

        'data/expiration_alert_document.xml',
        'data/sequence_code_document.xml',
        'data/sequence_code_download.xml',
        'data/documents_folder.xml',
    ],
    'assets': {
        'web.assets_backend': [
            's_document/static/src/views/*/*.js',
            's_document/static/src/views/*/*.xml',
            's_document/static/src/components/*/*.js',
            's_document/static/src/components/*/*.xml',
            's_document/static/src/css/custom_form_label.css',
        ]
    },
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook_remove_rule_core',
    'uninstall_hook': 'uninstall_hook_setup_rule_core'
}
