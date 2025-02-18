from odoo import api, fields, models, _


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _add_comment(self, validate_reject, reviews):
        wizard = self.env.ref("base_tier_validation.view_comment_wizard")
        return {
            "name": _("Reason for Approval/Denial"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "comment.wizard",
            "views": [(wizard.id, "form")],
            "view_id": wizard.id,
            "target": "new",
            "context": {
                "default_res_id": self.id,
                "default_res_model": self._name,
                "default_review_ids": reviews.ids,
                "default_validate_reject": validate_reject,
            },
        }

    def forward_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(lambda l: l.sequence in sequences)
        ctx = self._add_comment("forward", reviews)["context"]
        comment = (
            self.env["comment.wizard"].with_context(**ctx).create({"comment": "/"})
        )
        wizard = self.env.ref("base_tier_validation_forward.view_forward_wizard")
        return {
            "name": _("Approval Forward"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "tier.validation.forward.wizard",
            "views": [(wizard.id, "form")],
            "view_id": wizard.id,
            "target": "new",
            "context": {
                "default_res_id": self.id,
                "default_res_model": self._name,
                "comment_id": comment.id,
            },
        }

    def request_validation(self):
        if self._name == 'documents.document':
            td_obj = self.env["tier.definition"]
            tr_obj = self.env["tier.review"]
            vals_list = []
            for rec in self:
                if rec._check_state_from_condition() and rec.need_validation:
                    tier_definitions = td_obj.search(
                        [
                            ("model", "=", self._name),
                            ("company_id", "in", [False] + self.env.company.ids),
                        ],
                        order="sequence asc",
                    )
                    sequence = 0
                    for td in tier_definitions:
                        if rec.evaluate_tier(td):
                            sequence += 1
                            vals_list.append(rec._prepare_tier_review_vals(td, sequence))
                    self._update_counter({"review_created": True})
            created_trs = tr_obj.create(vals_list)
            self._notify_review_requested(created_trs)
            for rec in self:
                rec.update({
                    self._state_field: self._to_approve_state
                })
            return created_trs
        else:
            created_trs = super(TierValidation, self).request_validation()
            for rec in self:
                rec.update({
                    self._state_field: self._to_approve_state
                })
            return created_trs

    def _notify_requested_review_body(self):
        if self._name == 'documents.document' or self._name == 'download.documents':
            return _("Một yêu cầu duyệt tài liệu đã được tạo bởi %s.") % (self.env.user.name)
        else:
            super()._notify_requested_review_body()

    def _notify_accepted_reviews_body(self):
        if self._name == 'documents.document' or self._name == 'download.documents':
            has_review = self.review_ids.filtered(
                lambda r: (self.env.user in r.reviewer_ids)
            ).done_by.complete_name
            if has_review:
                if self._name == 'documents.document':
                    return _("Một yêu cầu upload đã được duyệt. (%s)") % has_review
                elif self._name == 'download.documents':
                    return _("Một yêu cầu download đã được duyệt. (%s)") % has_review
            return _("Một tài liệu đã được duyệt")
        else:
            super()._notify_accepted_reviews_body()

    def _notify_forwarded_reviews_body(self):
        if self._name == 'documents.document' or self._name == 'download.documents':
            has_comment = self.review_ids.filtered(
                lambda r: (self.env.user in r.reviewer_ids) and r.comment
            )
            if has_comment:
                comment = has_comment.mapped("comment")[0]
                return _("Một đánh giá đã được ủy quyền duyệt từ %(user_name)s %(comment)s") % (
                    {"user_name": self.env.user.name, "comment": comment}
                )
            return _("Một đánh giá đã được ủy quyền duyệt bởi %s.") % (self.env.user.name)
        else:
            super()._notify_forwarded_reviews_body()

    def _compute_next_review(self):
        if self._name == 'documents.document' or self._name == 'download.documents':
            for rec in self:
                review = rec.review_ids.sorted("sequence").filtered(
                    lambda x: x.status == "pending"
                )[:1]
                rec.next_review = review and _("Tiếp theo: %s") % review.name or ""
        else:
            super()._compute_next_review()
