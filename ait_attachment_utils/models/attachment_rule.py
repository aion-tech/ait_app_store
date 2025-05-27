import logging
from typing import Any, List, Literal, Tuple, Union

from markupsafe import Markup
from odoo import _, api, fields, models
from odoo.addons.attachment_utils.compression.utils import get_extension
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AttachmentRuleException(UserError):
    """ir.attachment.rule Violation"""


class IrAttachmentRule(models.Model):
    _name = "ir.attachment.rule"
    _description = "Attachment Rules"
    _rec_name = "model_id"
    _order = "sequence, id"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="If a record on a model matches multiple rules, the rule with the lowest sequence number will be applied.",
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        help="This rule will apply only to attachments linked to this model.",
    )
    domain = fields.Char(
        string="Domain",
        help="This rule will apply only to attachments linked to records that match this domain.",
    )

    # -- Extensions
    allowed_extensions = fields.Char(
        string="Allowed Extensions",
        help="Comma separated list of allowed file extensions",
    )
    forbidden_extensions = fields.Char(
        string="Forbidden Extensions",
        help="Comma separated list of forbidden file extesions",
    )

    # -- Maximum Size
    max_size = fields.Integer(
        string="Maximum Size (bytes)",
    )
    # warn_max_size = fields.Boolean(
    #     string="Warn if Above Maximum Size",
    #     default=False,
    #     help="Log a non-blocking warning if the file is above the maximum size. Can't be selected if Force Maximum Size is selected!",
    # )
    # force_max_size = fields.Boolean(
    #     string="Force Maximum Size",
    #     default=False,
    #     help="Raise if the file is above the maximum size."
    #          "If 'Compress' is enabled, attempt to compress it before raising.",
    # )
    try_compress = fields.Boolean(
        string="Compress",
        default=False,
        help="Attempt compression if the file is above the maximum size.",
    )

    # -- Minimum Size
    min_size = fields.Integer(
        string="Minimum Size (bytes)",
        default=-1,
    )
    # warn_min_size = fields.Boolean(
    #     string="Warn if Below Minimum Size",
    #     default=False,
    #     help="Log a non-blocking warning if the file is below the minimum size. Can't be selected if Force Minimum Size is selected!",
    # )
    # force_min_size = fields.Boolean(
    #     string="Force Minimum Size",
    #     default=False,
    #     help="Raise if the file is below the minimum size.",
    # )

    @api.onchange('warn_max_size', 'force_max_size', 'warn_min_size', 'force_min_size')
    def onchange_size_checks(self):
        if self.force_min_size:
            self.warn_min_size = False
        if self.force_max_size:
            self.warn_max_size = False

    def _eval_domain(self) -> Union[List[Union[str, Tuple[str, str, Any]]], None]:
        self.ensure_one()
        # TODO check domain syntax
        if self.domain:
            return safe_eval(self.domain)
        return None

    @api.constrains("model_id", "domain")
    def _check_conflicting_rules(self):
        """
        Rules should be unique per model and domain.
        """
        for rec in self:
            same_model_rules = self.search_count(
                [
                    ("model_id", "=", rec.model_id.id),
                    ("domain", "=", rec.domain),
                ]
            )
            if same_model_rules > 1:
                raise ValidationError(
                    f"Conflicting rules for model {rec.model_id.model} and domain {rec.domain}"
                )

    def _deserialize_extensions(self) -> Tuple[List, List]:
        self.ensure_one()
        allowed = self.allowed_extensions and self.allowed_extensions.split(",") or []
        forbidden = (
                self.forbidden_extensions and self.forbidden_extensions.split(",") or []
        )
        return allowed, forbidden

    @api.constrains("forbidden_extensions", "allowed_extensions")
    def _check_conflicting_extension_rules(self):
        for rec in self:
            allowed, forbidden = rec._deserialize_extensions()
            for ext in allowed:
                if ext in forbidden:
                    raise ValidationError(
                        "Can't allow and forbid the same extension at the same time!"
                    )

    def _build_error_msg(self, attachment) -> Union[List[str], None]:
        self.ensure_one()
        attachment.ensure_one()
        errors = []

        # -- Size error msg
        if self.max_size > 0 or self.min_size > -1:
            size_error_type = None
            if attachment.file_size > self.max_size:
                size_error_type = "max"
            if attachment.file_size < self.min_size:
                size_error_type = "min"
            if size_error_type:
                size_mb = f"{self.max_size / 1048576:.2f} MB" if size_error_type == "max" else f"{self.min_size / 1048576:.2f} MB"
                args: Tuple[str, str, str] = (
                    attachment.name,
                    "under" if size_error_type == "min" else "over",
                    # "minimum" if size_error_type == "min" else "maximum",
                    size_mb,
                )
                errors.append(_("%s is %s %s") % args)

        # -- Extensions error msg
        allowed, forbidden = self._deserialize_extensions()
        extension = get_extension(attachment.name)
        if allowed:
            if extension not in allowed:
                errors.append(
                    _("Allowed attachment extensions are: %s") % (",".join(allowed))
                )
        if forbidden:
            if extension in forbidden:
                errors.append(_("%s is not an allowed file extension") % (extension))

        return errors or None

    def _apply(self, attachments):
        self.ensure_one()
        for rec in attachments:
            errors = self._build_error_msg(rec)
            if not errors:
                continue
            if self.min_size > -1 or self.max_size > 0 or self.allowed_extensions or self.forbidden_extensions:
                for err in errors:
                    # self.env.user.notify_info(message=err, sticky=True)
                    _logger.warning(err)
                    raise AttachmentRuleException("\t".join(errors))
            # if self.warn_min_size or self.warn_max_size:
            #     error_message = "\t".join(errors)
            #     return {
            #         'type': 'ir.actions.client',
            #         'tag': 'display_notification',
            #         'params': {
            #             'title': 'Attenzione!',
            #             'message': error_message,
            #             'sticky': True,  # Se True, rimane finché l'utente non la chiude
            #             'type': 'warning',  # Tipi: 'success', 'warning', 'danger', 'info'
            #         }
            #     }
