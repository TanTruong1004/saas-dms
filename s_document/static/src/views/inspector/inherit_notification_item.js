/** @odoo-module */

import {session} from "@web/session";
import { NotificationItem } from "@mail/core/web/notification_item";
import { patch } from "@web/core/utils/patch";

patch(NotificationItem.prototype, {
    setup() {
        super.setup();
    },
    async onClick(ev) {
        if (typeof this.__owl__.key !== 'number' && this.__owl__.key !== undefined) {
            if (this.__owl__.key.includes('documents.document')) {
                const action = await this.env.services.orm.call("documents.document", "detail_documents_document_form", [parseInt(this.__owl__.key.split('AND').pop().trim())]);
                this.env.services.action.doAction(action);
            }
        }
        this.props.onClick(ev.target === this.markAsReadRef.el);
    }
})
