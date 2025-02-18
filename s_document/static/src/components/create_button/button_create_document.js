/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { DocumentsKanbanController } from "@documents/views/kanban/documents_kanban_controller";
import { DocumentsListController } from "@documents/views/list/documents_list_controller";

function setupPatch(originalSetup) {
    return function () {
        originalSetup.call(this);
        this.action = useService("action");
        this.dialogService = useService("dialog");
    };
}

function onClickCreateDocumentPatch(originalOnClickCreateDocument) {
    return async function () {
        if (originalOnClickCreateDocument) {
            await originalOnClickCreateDocument.call(this);
        }
        const action = await this.orm.call("documents.document", "create_documents_document_form", []);
        this.action.doAction(action);
    };
}

patch(DocumentsKanbanController.prototype, {
    setup: setupPatch(DocumentsKanbanController.prototype.setup),
    onClickCreateDocument: onClickCreateDocumentPatch(DocumentsKanbanController.prototype.onClickCreateDocument),
});

patch(DocumentsListController.prototype, {
    setup: setupPatch(DocumentsListController.prototype.setup),
    onClickCreateDocument: onClickCreateDocumentPatch(DocumentsListController.prototype.onClickCreateDocument),
});
