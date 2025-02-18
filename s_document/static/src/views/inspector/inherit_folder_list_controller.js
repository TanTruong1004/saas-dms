/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import {FolderListController} from "@documents/views/list/folder_list_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
patch(FolderListController.prototype, {
    setup() {
        super.setup();
    },
async onDeleteSelectedRecords() {
        const displayDialog = await this.orm.call(
            this.props.resModel,
            "is_folder_containing_document",
            [this.model.root.selection.map((record) => record.resId)]
        );
        if (displayDialog) {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Di chuyển vào thùng rác?"),
                body: _t(
                    "Bạn có muốn xóa vĩnh viễn không gian làm việc không ?",
                    this._deletionDelay
                ),
                confirmLabel: _t("Xóa"),
                confirm: async () => {
                    await this.orm.call(this.props.resModel, "action_archive", [
                        this.model.root.selection.map((record) => record.resId),
                    ]);
                    await this.model.load();
                },
                cancel: () => {},
            });
        } else {
            await this.orm.call(this.props.resModel, "action_archive", [
                this.model.root.selection.map((record) => record.resId),
            ]);
            await this.model.load();
        }
    }
});
