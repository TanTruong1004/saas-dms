/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentsKanbanController } from "@documents/views/kanban/documents_kanban_controller";
import { _t } from "@web/core/l10n/translation";

patch(DocumentsKanbanController.prototype, {
    onClickCreateDocuments() {
        this.action.doAction({
            name: _t("Create Document"),
            type: 'ir.actions.act_window',
            res_model: 'documents.create',
            views: [[false, 'form']],
            target: 'new',
            context: {
                default_folder_id: this.env.searchModel.getSelectedFolderId(),
            },
        });
    },
});
