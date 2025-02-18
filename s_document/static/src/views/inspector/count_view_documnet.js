/** @odoo-module **/
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import {DocumentsKanbanRecord} from "@documents/views/kanban/documents_kanban_model";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import {
    DocumentsModelMixin,
    DocumentsRecordMixin,
} from "@documents/views/documents_model_mixin";
patch(DocumentsKanbanRecord.prototype, {
    setup() {

        super.setup(...arguments);
    },
    async onClickPreview(ev) {
        if (this.data.type === "empty") {
            ev.stopPropagation();
            ev.target.querySelector(".o_kanban_replace_document").click();
        } else if (this.isViewable()) {
        if (this.data.mimetype.includes("image") || this.data.mimetype === 'application/pdf' || this.data.mimetype === 'video/mp4') {
               await this.model.env.services.orm.call(
                'documents.document',
                'increment_view_count',
                [this.data.id]
                );
            }
            ev.stopPropagation();
            ev.preventDefault();
            const folder = this.model.env.searchModel
                .getFolders()
                .filter((folder) => folder.id === this.data.folder_id[0]);
            const hasPdfSplit =
                (!this.data.lock_uid || this.data.lock_uid[0] === this.model.user.userId) &&
                folder.has_write_access;
            const selection = this.model.root.selection;
            const documents = selection.length > 1 && selection.find(rec => rec === this) && selection.filter(rec => rec.isViewable()) || [this];
            await this.model.env.documentsView.bus.trigger("documents-open-preview", {
                documents,
                mainDocument: this,
                isPdfSplit: false,
                rules: this.data.available_rule_ids.records,
                hasPdfSplit,
            });
        }
    },
    async onDragStart(ev) {
        if (this.resModel !== 'documents.document') {
            if (!this.selected) {
                this.onRecordClick(ev, { isKeepSelection: false, isRangeSelection: false });
            }
            const root = this.model.root;
            const foldersById = this.model.env.searchModel.getFolders().reduce((agg, folder) => {
                agg[folder.id] = folder;
                return agg;
            }, {});
            const draggableRecords = root.selection.filter(
                (record) => (!record.data.lock_uid || record.data.lock_uid[0] === this.context.uid) && foldersById[record.data.folder_id[0]].has_write_access
            );
            if (draggableRecords.length === 0) {
                ev.preventDefault();
                return;
            }
            const lockedCount = draggableRecords.reduce((count, record) => {
                return count + (record.data.lock_uid && record.data.lock_uid[0] !== this.context.uid);
            }, 0);
            ev.dataTransfer.setData(
                "o_documents_data",
                JSON.stringify({
                    recordIds: draggableRecords.map((record) => record.resId),
                    lockedCount,
                })
            );
            let dragText;
            if (draggableRecords.length === 1) {
                dragText = draggableRecords[0].data.name ? draggableRecords[0].data.display_name : _t("Unnamed");
            } else if (lockedCount > 0) {
                dragText = _t("%s Documents (%s locked)", draggableRecords.length, lockedCount);
            } else {
                dragText = _t("%s Documents", draggableRecords.length);
            }
            const newElement = document.createElement("span");
            newElement.classList.add("o_documents_drag_icon");
            newElement.innerText = dragText;
            document.body.append(newElement);
            ev.dataTransfer.setDragImage(newElement, -5, -5);
            setTimeout(() => newElement.remove());
        }
    }

});
