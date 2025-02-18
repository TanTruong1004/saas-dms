/** @odoo-module **/
import {session} from "@web/session";
import {patch} from "@web/core/utils/patch";
import {TierReviewMenu} from "@base_tier_validation/components/tier_review_menu/tier_review_menu.esm";

patch(TierReviewMenu.prototype, {
    setup() {
        super.setup();
    }
    ,
    async openReviewGroup(group) {
        document.body.click();
        if (group.model === "documents.document" || group.model === "download.documents") {
            const context = {"search_default_pending": true};
            let id_view = await this.env.services.orm.call(
                'documents.document',
                'check_view',
                ['']
            );

            let views = [[id_view, "list"]];

            if (group.model === 'download.documents') {
                this.action.doAction(
                    {
                        context,
                        domain: [["reviewer_ids", "in", this.env.services.user.userId], ['resource_type', '=', 'download.documents']],
                        name: 'Danh sách phê duyệt download của tôi',
                        res_model: 'tier.review',
                        search_view_id: [false],
                        type: "ir.actions.act_window",
                        views,
                    },
                    {
                        clearBreadcrumbs: true,
                    }
                );
            } else if (group.model === 'documents.document') {
                this.action.doAction(
                    {
                        context,
                        domain: [["reviewer_ids", "in", this.env.services.user.userId], ['resource_type', '=', 'documents.document']],
                        name: 'Danh sách phê duyệt upload của tôi',
                        res_model: 'tier.review',
                        search_view_id: [false],
                        type: "ir.actions.act_window",
                        views,
                    },
                    {
                        clearBreadcrumbs: true,
                    }
                );
            }
        }
        else {
            const context = {};
        var domain = [["can_review", "=", true]];
        if (group.active_field) {
            domain.push(["active", "in", [true, false]]);
        }
        const views = this.availableViews();

        this.action.doAction(
            {
                context,
                domain,
                name: group.name,
                res_model: group.model,
                search_view_id: [false],
                type: "ir.actions.act_window",
                views,
            },
            {
                clearBreadcrumbs: true,
            }
        );
        }
    }
});


