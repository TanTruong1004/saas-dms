/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import {Chatter} from "@mail/core/web/chatter";
import { useHover } from "@mail/utils/common/hooks";

patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.unfollowHover_orther_module = useHover("unfollow_other");
        this.unfollowdocument = useHover("unfollow_document");
    }
});
