import logging
from typing import Any, Union

from markupsafe import Markup
from odoo import _, api, fields, models
from odoo.addons.ait_attachment_utils.compression.utils import get_extension
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AttachmentRuleException(UserError):
    """Eccezione personalizzata per violazioni delle regole sugli allegati."""
    def __init__(self, message):
        super().__init__(message)


class IrAttachmentRule(models.Model):
    _name = "ir.attachment.rule"
    _description = "Attachment Rules"
    _rec_name = "model_id"
    _order = "sequence, id"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Lower sequence means higher priority among rules.",
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        help="This rule applies to attachments linked to this model.",
    )
    domain = fields.Char(
        string="Domain",
        help="Odoo domain expression for records to which this rule applies.",
    )

    allowed_extensions = fields.Char(
        string="Allowed Extensions",
        help="Comma-separated list of allowed file extensions.",
    )
    forbidden_extensions = fields.Char(
        string="Forbidden Extensions",
        help="Comma-separated list of forbidden file extensions.",
    )

    max_size = fields.Integer(string="Maximum Size (bytes)")
    try_compress = fields.Boolean(
        string="Compress",
        default=False,
        help="Attempt to compress the file if it exceeds max size.",
    )
    min_size = fields.Integer(
        string="Minimum Size (bytes)",
        default=-1,
    )

    def _eval_domain(self) -> Union[list, None]:
        self.ensure_one()
        if self.domain:
            try:
                return safe_eval(self.domain, {})
            except Exception as e:
                raise ValidationError(_("Invalid domain: %s") % str(e))
        return None

    @api.constrains("model_id", "domain")
    def _check_conflicting_rules(self):
        for rec in self:
            domain = rec.domain or False
            same_rules = self.search_count([
                ("model_id", "=", rec.model_id.id),
                ("domain", "=", domain),
            ])
            if same_rules > 1:
                raise ValidationError(
                    _("Conflicting rules for model %s and domain %s") % (
                        rec.model_id.model, domain)
                )

    def _deserialize_extensions(self) -> tuple[list[str], list[str]]:
        self.ensure_one()
        allowed = [ext.strip() for ext in (self.allowed_extensions or "").split(",") if ext.strip()]
        forbidden = [ext.strip() for ext in (self.forbidden_extensions or "").split(",") if ext.strip()]
        return allowed, forbidden

    @api.constrains("forbidden_extensions", "allowed_extensions")
    def _check_conflicting_extension_rules(self):
        for rec in self:
            allowed, forbidden = rec._deserialize_extensions()
            conflict = set(allowed) & set(forbidden)
            if conflict:
                raise ValidationError(
                    _("Extension(s) both allowed and forbidden: %s") % ", ".join(conflict)
                )

    def _build_error_msg(self, attachment) -> Union[list[str], None]:
        self.ensure_one()
        attachment.ensure_one()
        errors = []

        if self.max_size > 0 or self.min_size > -1:
            if self.max_size > 0 and attachment.file_size > self.max_size:
                size_mb = f"{self.max_size / 1048576:.2f} MB"
                errors.append(_("%s is over the maximum size of %s") % (attachment.name, size_mb))
            if self.min_size > -1 and attachment.file_size < self.min_size:
                size_mb = f"{self.min_size / 1048576:.2f} MB"
                errors.append(_("%s is under the minimum size of %s") % (attachment.name, size_mb))

        allowed, forbidden = self._deserialize_extensions()
        extension = get_extension(attachment.name)

        if allowed and extension not in allowed:
            errors.append(_("Only the following extensions are allowed: %s") % ", ".join(allowed))
        if forbidden and extension in forbidden:
            errors.append(_("Extension %s is not allowed") % extension)

        return errors or None

    def _apply(self, attachments: models.Model):
        self.ensure_one()
        for attachment in attachments:
            errors = self._build_error_msg(attachment)
            if errors:
                for err in errors:
                    _logger.warning(err)
                raise UserError("\n".join(errors))
