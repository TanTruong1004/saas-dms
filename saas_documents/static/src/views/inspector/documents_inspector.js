/** @odoo-module **/
import {session} from "@web/session";
import { useService } from '@web/core/utils/hooks';
import { patch } from "@web/core/utils/patch";
import dUtils from "@documents/views/helper/documents_utils";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";

import { inspectorFields, DocumentsInspector } from "@documents/views/inspector/documents_inspector";

inspectorFields.push("dbx_link",
"file_content","error_description_read", "error_description_push", "state_read", "state_push", "is_user_download",
                    "is_downloadable",
);

patch(DocumentsInspector.prototype,{
    setup() {
        super.setup();
        this.orm = useService('orm');
    },
    async onDownload() {
        const documents = this.props.documents.filter((rec) => rec.data.type !== "empty");
        if (!documents.length) {
            return;
        }
        const linkDocuments = documents.filter((el) => el.data.type === "url");
        const noLinkDocuments = documents.filter((el) => el.data.type !== "url");
        // Manage link documents
        if (documents.length === 1 && linkDocuments.length) {
            // Redirect to the link
            let url = linkDocuments[0].data.url;
            url = /^(https?|ftp):\/\//.test(url) ? url : "http://" + url;
            window.open(url, "_blank");
        } else if (noLinkDocuments.length) {
            if (documents[0].data.dbx_link) {
                   const result = await this.orm.call(
                    'documents.document',
                    'download_file',
                    [documents[0].data.id]
                    );
                    window.open(result.url, "_blank");
             }
            // Download all documents which are not links
            else{
             this.download(noLinkDocuments);
            }

        }
    },

    getFieldProps(fieldName, additionalProps) {
        const rec = this.props.documents[0];
        const record = Object.create(rec.constructor.prototype);
        Object.assign(record, rec);

        const props = {
            record: record,
            name: fieldName,
            documents: [...this.props.documents],
            inspectorReadonly: true,
            lockAction: this.doLockAction.bind(this),
        };
        if (fieldName === 'create_date') {
            this.props.fields.create_date.type = "date";
        }
        if (additionalProps) {
            Object.assign(props, additionalProps);
        }
        return props;
    },

    async on_Share() {
        const supportedTypes = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword", "application/vnd.oasis.opendocument.text", "application/rtf", "text/plain",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel",
         "application/vnd.oasis.opendocument.spreadsheet", "text/csv", "application/pdf"];
        const isSupportedType = supportedTypes.includes(this.props.documents[0]._values.mimetype);
        if (isSupportedType) {
            const documents = this.props.documents[0];
            const action = await this.orm.call("documents.document", "open_user_access_popup", [documents.data.id]);
            this.action.doAction(action)

        } else {
            const resIds = this.props.documents

                        .filter((rec) => rec._values.type !== "empty")
                        .map((rec) => rec._values.id);

                    const linkProportion = await dUtils.get_link_proportion(this.orm, resIds ? resIds : false);
                    if (!this.generatedUrls[resIds]) {
                        const vals = await this.createShareVals();
                        this.generatedUrls[resIds] = await this.orm.call(
                            "documents.share",
                            "action_get_share_url",
                            [vals]
                        );
                    }
                    setTimeout(async () => {
                        await browser.navigator.clipboard.writeText(this.generatedUrls[resIds]);
                        if (linkProportion == "some") {
                            this.notificationService.add(
                                _t("The share url has been copied to your clipboard. Links were excluded."),
                                { type: "warning" }
                            );
                        } else {
                            this.notificationService.add(_t("The share url has been copied to your clipboard."), {
                                type: "success",
                            });
                        }
                    });
            }
    }
});
