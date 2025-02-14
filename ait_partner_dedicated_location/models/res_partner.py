from odoo import models, fields, api, _
from odoo.exceptions import *

RES_PARTNER = 'res.partner'
DEDICATED_CUSTOMER_LOCATION = 'dedicated_customer_location'
DEDICATED_VENDOR_LOCATION = 'dedicated_vendor_location'
DEDICATED_SUB_LOCATION = 'dedicated_subcontracting_location'
LOCATION_ID = 'location_id'
NAME = 'name'


class RidixResPartner(models.Model):
    _inherit = RES_PARTNER
    _description = RES_PARTNER

    dedicated_customer_location = fields.Boolean(string='Dedicated Customer Location',
                                                 default=False)

    dedicated_vendor_location = fields.Boolean(string='Dedicated Vendor Location',
                                               default=False)

    dedicated_subcontracting_location = fields.Boolean(string='Dedicated Subcontracting Location',
                                                       default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get(DEDICATED_CUSTOMER_LOCATION):
                self._create_location(vals, 'customer_parent')
            if vals.get(DEDICATED_VENDOR_LOCATION):
                self._create_location(vals, 'vendor_parent')
            if vals.get(DEDICATED_SUB_LOCATION):
                self._create_location(vals, 'subcontracting_parent')

        return super().create(vals_list)

    def _check_dedicated_location(self, dedicated_location):
        var = self.env['res.config'].sudo().get_values()
        parent_id = var.get(dedicated_location) or False
        if not parent_id:
            raise UserError(
                _("Missing warehouse configuration!\nAdd custom route in warehouse settings."))
        return parent_id

    def _create_location(self, vals, parent):
        parent_id = self._check_dedicated_location(parent)
        location_env = self.env['stock.location']
        warehouse = location_env.sudo().search([(NAME, '=', vals.get(NAME)),
                                                (LOCATION_ID, '=', parent_id)])
        if not warehouse:
            location_env.create({
                NAME: vals.get(NAME),
                LOCATION_ID: parent_id,
                'usage': 'internal'
            })
