from odoo import models


class CommentWizard(models.TransientModel):
    _inherit = "comment.wizard"

    def add_comment(self):
        if self.res_model == 'documents.document':
            self.ensure_one()
            rec = self.env[self.res_model].browse(self.res_id)
            review_id = self.review_ids.filtered(lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids))
            review_id.write({"comment": self.comment})
            if self.validate_reject == "validate":
                rec._validate_tier(self.review_ids)
            if self.validate_reject == "reject":
                rec._rejected_tier(self.review_ids)
            rec._update_counter({"review_deleted": True})

            rec = self.env[self.res_model].browse(self.res_id)
            if self.validate_reject == "forward":
                rec._forward_tier(self.review_ids)
            rec._update_counter({"review_created": True})
            return self.review_ids
        else:
            super().add_comment()
            rec = self.env[self.res_model].browse(self.res_id)
            if self.validate_reject == "forward":
                rec._forward_tier(self.review_ids)
            rec._update_counter({"review_created": True})
            return self.review_ids
