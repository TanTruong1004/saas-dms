/** @odoo-module **/

import {registry} from '@web/core/registry';
import {session} from '@web/session';
import {browser} from '@web/core/browser/browser';

const langService = {
    dependencies: ['orm', 'action'],
    start(env, {orm, action}) {

        async function getLangs() {
            return await orm.searchRead(
                'res.lang', [],
                [
                    'name',
                    'code',
                    'iso_code',
                    'url_code',
                ]
            )
        }

        async function setLang(lang) {
            const currentLang = session.bundle_params.lang;
            if (lang.code === currentLang) return

            await orm.write('res.users', [session.uid], {
                lang: lang.code,
            });
            action.doAction('reload_context')
        }

        return {
            getLangs,
            setLang,
        }
    }
};

registry.category('services').add('lang', langService);
