/* @odoo-module */

import { Message } from "@mail/core/common/message";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(Message.prototype, {
    setup() {
        super.setup(...arguments);
    },
        formatTrackingOrNone(trackingType, trackingValue) {
        let formattedValue = this.formatTracking(trackingType, trackingValue);
        if (this.env.searchModel !== undefined) {
            if (this.env.searchModel.resModel === "documents.document" || this.env.searchModel.resModel === "download.documents") {
                if (formattedValue === "Rejected" || formattedValue === "In Progress") {
                    formattedValue = formattedValue === "Rejected" ? "Từ chối" : "Đang phê duyệt";
                }
            }
        }
        return formattedValue || _t("None");
    },
})
