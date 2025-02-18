/** @odoo-module **/
import {session} from "@web/session";
import { useService } from '@web/core/utils/hooks';
import { patch } from "@web/core/utils/patch";
import {
    inspectorFields,
    DocumentsInspector,
} from "@documents/views/inspector/documents_inspector";

inspectorFields.push("issuing_authority",
                    "completed_name",
                    "document_code",
                    "release_date",
                    "expiration_date",
                    "document_type",
                    "version",
                    "document_description",
                    'write_date',
);
patch(DocumentsInspector.prototype,{
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.action = useService("action");
    },
     async onOpenDocument() {
        const record = this.props.documents[0];
        let id_view = await this.orm.call(
            record.data.res_model,
            "action_open_document_form",
            [record.data.res_id]
        );
        this.action.doAction(
            {
                id: id_view.id,
                type: "ir.actions.act_window",
                name: id_view.name,
                res_model: "documents.document",
                views: [[id_view.view_id, "form"]],
                view_mode: "form",
                target: "current",
                res_id: id_view.res_id
            }
        );
    }
});
