/** @odoo-module **/
import {session} from "@web/session";
import { patch } from "@web/core/utils/patch";
import {ActivityMenu} from "@mail/core/web/activity_menu";
patch(ActivityMenu.prototype,{
    setup() {
        super.setup();
    }
    ,
    openActivityGroup(group, filter="all") {
        let view_type = group.model === 'documents.document' ? "kanban" : group.viewType
        document.body.click(); // hack to close dropdown
        const context = {
            // Necessary because activity_ids of mail.activity.mixin has auto_join
            // So, duplicates are faking the count and "Load more" doesn't show up
            force_search_count: 1,
        };
        if (group.model === "mail.activity") {
            this.action
                .doAction("mail.mail_activity_without_access_action", {
                    additionalContext: {
                        active_ids: group.activity_ids,
                    },
                })
                .catch((error) => {
                    if (error instanceof RPCError) {
                        this.action.doAction("mail.mail_activity_action", {
                            additionalContext: {
                                active_ids: group.activity_ids,
                            },
                        });
                    }
                });
            return;
        }

        if (filter === "all") {
            context["search_default_activities_overdue"] = 1;
            context["search_default_activities_today"] = 1;
        }
        else if(filter === "overdue"){
            context["search_default_activities_overdue"] = 1;
        }
        else if(filter === "today"){
            context["search_default_activities_today"] = 1;
        }
        else if(filter === "upcoming_all"){
            context["search_default_activities_upcoming_all"] = 1;
        }


        let domain = [["activity_user_id", "=", this.userId]];
        if (group.domain) {
            domain = Domain.and([domain, group.domain]).toList();
        }
        const views = this.availableViews(group);

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
                viewType: view_type,
            }
        );
    }
});


