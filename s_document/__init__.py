# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import wizard


def post_init_hook_remove_rule_core(env):
    env['ir.rule'].search([('name', '=', 'Documents.document: folder write groups')], limit=1).write({
        'active': False,
    })
    env['ir.rule'].search([('name', '=', 'Documents.document: global')], limit=1).write({
        'active': False,
    })
    env['ir.rule'].search([('name', '=', 'Documents.document: readonly rule')], limit=1).write({
        'active': False,
    })


def uninstall_hook_setup_rule_core(env):
    env['ir.rule'].search([('name', '=', 'Documents.document: folder write groups')], limit=1).write({
        'active': True,
    })
    env['ir.rule'].search([('name', '=', 'Documents.document: global')], limit=1).write({
        'active': True,
    })
    env['ir.rule'].search([('name', '=', 'Documents.document: readonly rule')], limit=1).write({
        'active': True,
    })
