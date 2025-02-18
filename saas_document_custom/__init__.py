from . import models

def delete_document_rule(env):
    env['ir.rule'].search([('name', '=', 'Documents.document: readonly rule inherit')], limit=1).write({
        'active': False,
    })
    env['ir.rule'].search([('name', '=', 'Documents: readonly rule inherit')], limit=1).write({
        'active': False,
    })


def setup_document_rule(env):
    env['ir.rule'].search([('name', '=', 'Documents.document: readonly rule inherit')], limit=1).write({
        'active': True,
    })
    env['ir.rule'].search([('name', '=', 'Documents: readonly rule inherit')], limit=1).write({
        'active': True,
    })
