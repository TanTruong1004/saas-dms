/** @odoo-module **/

import {Dropdown} from '@web/core/dropdown/dropdown';
import {DropdownItem} from '@web/core/dropdown/dropdown_item';
import {useService} from '@web/core/utils/hooks';
import {registry} from '@web/core/registry';

import {Component, onWillStart} from '@odoo/owl';

import {session} from '@web/session';

export class SwitchLanguageMenu extends Component {
    setup() {
        this.langService = useService('lang');
        this.userLangCode = session.bundle_params.lang;

        onWillStart(async () => {
            this.langs = await this.langService.getLangs();
            this.lang = this.langs.find(l => l.code === this.userLangCode);
        })
    }

    async switch(lang) {
        this.langService.setLang(lang);
    }
}

SwitchLanguageMenu.template = 'web_systray_language.SwitchLanguageMenu';
SwitchLanguageMenu.components = {Dropdown, DropdownItem};


export const languageSystrayItem = {
    Component: SwitchLanguageMenu,
};

registry.category('systray').add('SwitchLanguageMenu', languageSystrayItem, {sequence: 1});
