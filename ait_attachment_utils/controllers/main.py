import logging

from odoo import _, http
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.addons.mail.controllers.attachment import AttachmentController
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.addons.mail.tools.discuss import Store

_logger = logging.getLogger(__name__)


class AttachmentUtilsDiscussController(AttachmentController):

    @http.route("/mail/attachment/upload", methods=["POST"], type="http", auth="public")
    @add_guest_to_context
    def mail_attachment_upload(self, ufile, thread_id, thread_model, is_pending=False, **kwargs):
        attachment_data = {}

        try:
            # Verifica accesso se si tratta di un canale
            if thread_model == "mail.channel":
                channel = request.env["mail.channel"].sudo().browse(int(thread_id))
                if not channel._channel_fetch_membership():
                    raise AccessError(_("You are not allowed to access this channel."))

            # Prepara i dati dell'allegato
            vals = {
                "name": ufile.filename,
                "raw": ufile.read(),
                "res_id": int(thread_id),
                "res_model": thread_model,
            }

            if is_pending and is_pending != "false":
                vals.update({
                    "res_id": 0,
                    "res_model": "mail.compose.message",
                })

            if request.env.user.share:
                vals["access_token"] = request.env["ir.attachment"]._generate_access_token()

            # Crea l'allegato
            attachment = request.env["ir.attachment"].sudo().create(vals)
            attachment._post_add_create(**kwargs)

            # Prepara risposta dati allegato
            attachment_data = {"data": Store(attachment, extra_fields=["access_token"]).get_result()}

        except AccessError:
            _logger.warning("AccessError during attachment upload")
            attachment_data = {
                "error": _("You are not allowed to upload an attachment here.")
            }

        except UserError as ue:
            _logger.warning("UserError during attachment upload: %s", ufile.filename)
            attachment_data = {
                "error": str(ue)
            }

        except Exception as e:
            _logger.exception("Unexpected error during attachment upload")
            attachment_data = {
                "error": _("Unexpected server error: %s") % str(e)
            }

        response = request.make_json_response(attachment_data)
        return response
