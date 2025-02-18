/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import {DocumentsActionHelper} from "@documents/views/helper/documents_action_helper";
import { markup } from "@odoo/owl";
import { escape } from "@web/core/utils/strings";
import { _t } from "@web/core/l10n/translation";

patch(DocumentsActionHelper.prototype, {
    setup() {
        super.setup();
    },
        get noContentHelp() {
        if (!this.selectedFolderId || this.selectedFolderId === "TRASH") {
            return markup(
                `<p class='o_view_nocontent_smiling_face'>
                    ${escape(
                        this.selectedFolderId === "TRASH"
                            ? _t("Các tài liệu đã xóa sẽ hiển thị ở đây")
                            : _t("Chọn một không gian làm việc để tải lên tài liệu.")
                    )}
                </p>`
            );
        }
        return this.props.noContentHelp;
    }
});
