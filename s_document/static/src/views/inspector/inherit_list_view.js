/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { patch } from "@web/core/utils/patch";

patch(listView, {
    display_name: "Danh sách",
});

const customListView = {
    ...listView,
    display_name: "Danh sách",
};

registry.category("views").add("custom_list", customListView);
