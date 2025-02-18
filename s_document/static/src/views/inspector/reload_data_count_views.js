/** @odoo-module **/
import {session} from "@web/session";
import { patch } from "@web/core/utils/patch";
import {FileViewer} from "@web/core/file_viewer/file_viewer";

patch(FileViewer.prototype,{
    setup() {
        super.setup();
    },
    close() {
        if(this.env.model !== undefined){
        if (this.env.model.root.resModel === "documents.document") {
            location.reload(true);
        }}
        this.props.close && this.props.close();
    }
});


