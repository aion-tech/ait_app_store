from odoo import _, http
from odoo.addons.ait_attachment_utils.models.attachment_rule import AttachmentRuleException
from odoo.addons.mail.controllers.discuss import DiscussController
from odoo.exceptions import AccessError, UserError
from odoo.http import request


class AttachmentUtilsDiscussController(DiscussController):

    @http.route("/mail/attachment/upload", methods=["POST"], type="http", auth="public")
    def mail_attachment_upload(
        self, ufile, thread_id, thread_model, is_pending=False, **kwargs
    ):
        channel_member = request.env["mail.channel.member"]
        if thread_model == "mail.channel":
            channel_member = request.env[
                "mail.channel.member"
            ]._get_as_sudo_from_request_or_raise(
                request=request, channel_id=int(thread_id)
            )
        vals = {
            "name": ufile.filename,
            "raw": ufile.read(),
            "res_id": int(thread_id),
            "res_model": thread_model,
        }
        if is_pending and is_pending != "false":
            # Add this point, the message related to the uploaded file does
            # not exist yet, so we use those placeholder values instead.
            vals.update(
                {
                    "res_id": 0,
                    "res_model": "mail.compose.message",
                }
            )
        if channel_member.env.user.share:
            # Only generate the access token if absolutely necessary (= not for internal user).
            vals["access_token"] = channel_member.env[
                "ir.attachment"
            ]._generate_access_token()
        try:
            attachment = channel_member.env["ir.attachment"].create(vals)
            attachment._post_add_create()
            attachmentData = {
                "filename": ufile.filename,
                "id": attachment.id,
                "mimetype": attachment.mimetype,
                "name": attachment.name,
                "size": attachment.file_size,
            }
            if attachment.access_token:
                attachmentData["accessToken"] = attachment.access_token
        except AccessError:
            attachmentData = {
                "error": _("You are not allowed to upload an attachment here.")
            }
        except AttachmentRuleException as e:
            attachmentData = {
                "error": e,
            }
        return request.make_json_response(attachmentData)
