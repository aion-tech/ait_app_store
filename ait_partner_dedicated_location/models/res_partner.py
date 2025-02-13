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

    # Overridden create method
    @api.model_create_multi
    def create(self, vals_list):
        # Loop through each set of values in the list
        for vals in vals_list:
            # Check if dedicated customer location is specified and set to True
            if vals.get(DEDICATED_CUSTOMER_LOCATION) and vals.get(DEDICATED_CUSTOMER_LOCATION) == True:
                # Create the location using _create_location method with 'customer_parent' as the location type
                self._create_location(vals, 'customer_parent')

            # Check if dedicated vendor location is specified and set to True
            if vals.get(DEDICATED_VENDOR_LOCATION) and vals.get(DEDICATED_VENDOR_LOCATION) == True:
                # Create the location using _create_location method with 'vendor_parent' as the location type
                self._create_location(vals, 'vendor_parent')

            # Check if dedicated subcontracting location is specified and set to True
            if vals.get(DEDICATED_SUB_LOCATION) and vals.get(DEDICATED_SUB_LOCATION) == True:
                # Create the location using _create_location method with 'subcontracting_parent' as the location type
                self._create_location(vals, 'subcontracting_parent')

        # Call the create method of the parent class to perform the actual creation of the records
        res = super(RidixResPartner, self).create(vals_list)

        # Return the result of the create method
        return res

    # Helper method to check and get the parent ID based on configuration
    def _check_dedicated_location(self, dedicated_location):
        # Retrieve values from the configuration settings using sudo to bypass access rights
        var = self.env['res.config.settings'].sudo().get_values()

        # Get the parent_id from the configuration settings based on the dedicated_location parameter
        parent_id = var.get(dedicated_location) if var.get(
            dedicated_location) else False

        # If parent_id is not found, raise a UserError with a specific message
        if not parent_id:
            raise UserError(
                _("Missing warehouse configuration!\nAdd custom route in warehouse settings."))

        # Return the obtained parent_id
        return parent_id

    # Helper method to create a location based on given values and parent
    def _create_location(self, vals, parent):
        # Check if a dedicated location exists for the parent
        parent_id = self._check_dedicated_location(parent)

        # Get the environment for stock locations
        location_env = self.env['stock.location']

        # Search for existing warehouse with the given name and parent location ID
        warehouse = location_env.sudo().search([(NAME, '=', vals.get(NAME)),
                                                (LOCATION_ID, '=', parent_id)])

        # If warehouse with the same name and parent ID does not exist, create a new one
        if not warehouse:
            location_env.create({
                NAME: vals.get(NAME),
                LOCATION_ID: parent_id,
                'usage': 'internal'
            })
