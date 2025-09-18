import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def _find_applicable_rule(self, res_model=None, res_id=None):
        """
        Find the first applicable rule for this attachment.
        """
        if res_model is None:
            res_model = self.res_model
        if res_id is None:
            res_id = self.res_id

        if res_model and res_id:
            res = self.env[res_model].browse([res_id])
            ir_model = self.env["ir.model"].search([("model", "=", res_model)])
            rules = self.env["ir.attachment.rule"].search(
                [("model_id", "=", ir_model.id)],
                order="sequence",
            )
            if not rules:
                return None
            for rule in rules:
                domain = rule._eval_domain()
                if domain:
                    if res.filtered_domain(domain):
                        return rule
                    else:
                        continue
                return rule

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            rule = self._find_applicable_rule(val.get('res_model'), val.get('res_id'))
            if not rule:
                continue
            virtual_attachment = self.new(val)
            virtual_attachment._inverse_datas()
            rule._apply(virtual_attachment)

        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rule = rec._find_applicable_rule()
            if not rule:
                continue
            rule._apply(rec)
        return res
