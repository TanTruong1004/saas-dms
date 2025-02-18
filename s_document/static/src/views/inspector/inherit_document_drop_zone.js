/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import {DocumentsDropZone} from "@documents/views/helper/documents_drop_zone";
import { useHover } from "@mail/utils/common/hooks";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";


patch(DocumentsDropZone.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
    },
    async onDrop(ev) {
        if (!ev.dataTransfer.types.includes("Files")) {
            return;
        }

        const files = ev.dataTransfer.files;
        let is_approve = await this.orm.call(
            'documents.folder',
            'check_is_approve',
            [this.env.searchModel.getSelectedFolderId()]
        );

        if (this.env.searchModel.resModel === 'documents.document') {
            if (is_approve) {
                window.alert(_t("This feature cannot be used"));
                window.location.reload();
            } else {
                this.root?.el?.classList.remove(this.rootDropOverClass);
                this.state.dragOver = false;

                if (this.isFolder) {
                    this.env.documentsView.bus.trigger("documents-upload-files", {
                        files: files,
                        folderId: this.env.searchModel.getSelectedFolderId(),
                        recordId: false,
                        tagIds: this.env.searchModel.getSelectedTagIds(),
                    });
                }
            }
        }
    }
});
