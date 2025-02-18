/** @odoo-module **/
import {session} from "@web/session";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";
import {useState, onWillStart} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {RemainingDaysField} from "@web/views/fields/remaining_days/remaining_days_field";

patch(RemainingDaysField.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.state = useState({remind_date: 0})
        onWillStart(() => this.loadConfig());
    },
    async loadConfig() {
        if (this.props.record.resModel === 'documents.document' || this.props.record.resModel === 'download.documents') {
            try {
                let remind_date = await this.orm.call(
                    'documents.document',
                    'get_param_config_remind_date',
                    ['']
                );
                Object.assign(this.state, {remind_date: remind_date});
            } catch (error) {
                console.error("Error calling get_param_config_remind_date:", error);
            }
        }
    },
    get diffString() {
        let Yesterday = "Yesterday"
        let Today = "Today"
        let Tomorrow = "Tomorrowss"
        let day_ago = "%s days ago"
        let in_day = "In %s days";
        if (this.props.record.resModel === 'documents.document') {
            let currentDate = new Date();
            let [day, month, year] = this.formatted.split('/').map(Number);

            let date1 = new Date(year, month - 1, day);

            currentDate.setDate(currentDate.getDate() + this.state.remind_date);
            Yesterday = "Expired yesterday";
            Today = "Expires today";
            Tomorrow = "Expires tomorrow";
            day_ago = "%s days ago";
            in_day = "%s days remaining";

            if (currentDate.setHours(0, 0, 0, 0) < date1.setHours(0, 0, 0, 0)) {
                return this.formattedValue;
            }
        }
        if (this.diffDays === null) {
            return "";
        }
        switch (this.diffDays) {
            case -1:
                return _t(Yesterday);
            case 0:
                return _t(Today);
            case 1:
                return _t(Tomorrow);
        }
        if (Math.abs(this.diffDays) > 99) {
            return this.formattedValue;
        }
        if (this.diffDays < 0) {
            return _t(day_ago, -this.diffDays);
        }
        return _t(in_day, this.diffDays);
    }
});
