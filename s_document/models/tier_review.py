from odoo import api, fields, models, _
from datetime import datetime, timedelta
import pytz
from odoo.exceptions import ValidationError


class TierReview(models.Model):
    _inherit = "tier.review"

    is_emergency = fields.Boolean(string='Emergency')
    code_system = fields.Char(string='Code')
    approval_date = fields.Date('Approval Date')
    issuing_authority = fields.Char(string='Issuing Authority')
    document_type = fields.Char(string='Document Category')
    document_code = fields.Char(string='Document Code')
    completed_name = fields.Text(string='Document Name')
    custom_update_date = fields.Date('Last Edited')
    release_date = fields.Date(string='Release Date')
    expiration_date = fields.Date(string='Expiration Date')
    version = fields.Char(string='Version')
    check_request_approval_date = fields.Integer('Check Request Approval Date', compute='_check_request_approval_date')

    def action_open_resource_ref(self):
        if self.model == 'documents.document':
            return {
                "name": self.resource_ref.display_name,
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                'views': [(self.env.ref('s_document.view_sdocument_document_view_new_form').id, 'form')],
                "res_model": self.model,
                'id': self.env.ref('documents.document_action').id,
                "res_id": self.res_id,
            }
        return super(TierReview, self).action_open_resource_ref()

    def _compute_reviewed_formated_date(self):
        timezone = self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        for review in self:
            if review.model == 'documents.document' or review.model == 'download.documents':
                if not review.reviewed_date:
                    review.reviewed_formated_date = False
                    continue
                reviewed_date_utc = pytz.timezone("UTC").localize(review.reviewed_date)
                reviewed_date_tz = reviewed_date_utc.astimezone(pytz.timezone(timezone))
                review.reviewed_formated_date = reviewed_date_tz.replace(tzinfo=None).strftime("%d/%m/%Y")
            else:
                super(TierReview, self)._compute_reviewed_formated_date()

    @api.depends("model", "res_id")
    def _compute_resource_ref(self):
        for rec in self:
            if rec.model in ['documents.document', 'download.documents']:
                rec.resource_ref = (
                    "%s,%s" % (rec.model, rec.res_id) if rec.res_id else False
                )
                resource = rec.resource_ref if rec.model == 'documents.document' else rec.resource_ref.document_id
                rec.resource_name = resource.name
                rec.is_emergency = resource.is_emergency
                rec.code_system = resource.code_system
                rec.issuing_authority = resource.issuing_authority.name
                rec.document_type = resource.document_type.name
                rec.document_code = resource.document_code
                rec.completed_name = resource.name
                rec.custom_update_date = resource.custom_update_date
                rec.release_date = resource.release_date
                rec.expiration_date = resource.expiration_date
                rec.version = resource.version
                rec.resource_type = rec.model
                rec.next_review = resource.next_review
            else:
                return super(TierReview, self)._compute_resource_ref()

    def _schedule_review_reminder_activity(self, record):
        if self.model == 'documents.document':
            record.activity_schedule(
                act_type_xmlid=self._get_reminder_activity_type(),
                note=self._notify_review_reminder_body(),
                user_id=self.reviewer_ids.id
            )
        else:
            return super(TierReview, self)._schedule_review_reminder_activity(record)

    @api.depends('approval_date')
    def _check_request_approval_date(self):
        for record in self:
            if record.model == 'documents.document' or record.model == 'download.documents':
                if record.approval_date:
                    delta = (record.approval_date - fields.Date.today()).days
                    record.check_request_approval_date = True if delta == 1 else False
                    if (record.approval_date - fields.Date.today()).days <= 0:
                        record.check_request_approval_date = True
                else:
                    record.check_request_approval_date = False

    def create(self, values):
        if type(values) == dict:
            remind_date = self.env['tier.definition'].search(
                [('document_id', '=', values['res_id']),
                 ('reviewer_id', '=', values['requested_by'])]).notify_reminder_delay
            values['approval_date'] = self._get_date_remind(values, remind_date)
        else:
            for value in values:
                remind_date = self.env['tier.definition'].search(
                    [('id', '=', value['definition_id'])]).notify_reminder_delay
                value['approval_date'] = self._get_date_remind(value, remind_date)
        return super(TierReview, self).create(values)


    def _get_date_remind(self, record, remind_date):
        if remind_date != 0 and record['model'] == 'documents.document' or record['model'] == 'download.documents':
            return datetime.now().date() + timedelta(days=remind_date)
        return None

    def _get_reviewers(self):
        if self.definition_id and self.definition_id.get_head_of_department:
            main_request = self.env[self.model].browse(self.res_id)
            created_employee = main_request.create_uid.employee_id
            if created_employee:
                head = created_employee.get_head_of_department()
                if head:
                    deputy = head.get_deputies(self.model)
                    if deputy:
                        return head.user_id + deputy.user_id
                    else:
                        return head.user_id
                else:
                    raise ValidationError(f'Employee {str(created_employee.name)} do not have Head of function')
            else:
                raise ValidationError(f'Employee of User ({main_request.create_uid.login}) does not exist')

        elif self.definition_id and self.definition_id.get_manager_of_department:
            request = self.env[self.model].browse(self.res_id)
            employee_created = request.create_uid.employee_id
            if employee_created:
                manager = employee_created.get_manager_of_department()
                if manager:
                    return manager.user_id
                else:
                    raise ValidationError(_("The Employee - %s has not Manager") % employee_created.name)
            else:
                raise ValidationError(f'Employee of User ({request.create_uid.login}) does not exist')
        elif self.definition_id.approve_request:
            company_id = self.definition_id.document_id.issuing_authority.id if self.definition_id.document_id else self.definition_id.download_id.document_id.issuing_authority.id
            employee = self.env['hr.employee'].search(
                [('id', '=', self.definition_id.reviewer_id.employee_id.parent_id.id), ('company_id', '=', company_id)],
                limit=1)
            created_employee = self.definition_id.reviewer_id
            if employee:
                return employee.user_id + created_employee
            else:
                return created_employee
        return super(TierReview, self)._get_reviewers()
