from odoo import models, fields, api, _
from odoo.exceptions import *

RES_PARTNER = 'res.partner'
DEDICATED_CUSTOMER_LOCATION = 'dedicated_customer_location'
DEDICATED_VENDOR_LOCATION = 'dedicated_vendor_location'
DEDICATED_SUB_LOCATION = 'dedicated_subcontracting_location'
DEDICATED_RENTAL_LOCATION = 'dedicated_rental_location'
LOCATION_ID = 'location_id'
NAME = 'name'


class AitStockLocationResPartner(models.Model):
    _inherit = RES_PARTNER
    _description = RES_PARTNER

    dedicated_customer_location = fields.Boolean(string='Dedicated Customer Location',
                                                 default=False)

    dedicated_vendor_location = fields.Boolean(string='Dedicated Vendor Location',
                                               default=False)

    dedicated_subcontracting_location = fields.Boolean(string='Dedicated Subcontracting Location',
                                                       default=False)

    dedicated_rental_location = fields.Boolean(string='Dedicated Rental Location',
                                               default=False)

    dedicated_customer_location_created = fields.Boolean(string='Dedicated Rental Location Created',
                                               default=False)

    dedicated_vendor_location_created = fields.Boolean(string='Dedicated Vendor Location Created',
                                               default=False)

    dedicated_subcontracting_location_created = fields.Boolean(string='Dedicated Subcontracting Location Created',
                                                       default=False)

    dedicated_rental_location_created = fields.Boolean(string='Dedicated Rental Location Created',
                                               default=False)

    property_stock_rental = fields.Many2one(
        'stock.location', string="Ubicazione noleggio", company_dependent=True, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]")

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

            # Check if dedicated rental location is specified and set to True
            if vals.get(DEDICATED_RENTAL_LOCATION) and vals.get(DEDICATED_RENTAL_LOCATION) == True:
                # Create the location using _create_location method with 'subcontracting_parent' as the location type
                self._create_location(vals, 'rental_parent')

        # Call the create method of the parent class to perform the actual creation of the records
        res = super(AitStockLocationResPartner, self).create(vals_list)
        for record in res:
            if res.dedicated_subcontracting_location:
                parent_id = self._check_dedicated_location('subcontracting_parent')
                sub_vendor_location = self.env['stock.location'].search([
                    ('location_id', '=', parent_id),
                    ('name', '=', record.name)
                ])
                if sub_vendor_location:
                    record.property_stock_subcontractor = sub_vendor_location[0]
                    record.dedicated_subcontracting_location_created = True

            if res.dedicated_vendor_location:
                parent_id = self._check_dedicated_location('vendor_parent')
                vendor_location = self.env['stock.location'].search([
                    ('location_id', '=', parent_id),
                    ('name', '=', record.name)
                ])
                if vendor_location:
                    record.property_stock_supplier = vendor_location[0]
                    record.dedicated_vendor_location_created = True

            if res.dedicated_customer_location:
                parent_id = self._check_dedicated_location('customer_parent')
                customer_location = self.env['stock.location'].search([
                    ('location_id', '=', parent_id),
                    ('name', '=', record.name)
                ])
                if customer_location:
                    record.property_stock_customer = customer_location[0]
                    record.dedicated_customer_location_created = True

            if res.dedicated_rental_location:
                parent_id = self._check_dedicated_location('rental_parent')
                rental_location = self.env['stock.location'].search([
                    ('location_id', '=', parent_id),
                    ('name', '=', record.name)
                ])
                if rental_location:
                    record.property_stock_rental = rental_location[0]
                    record.dedicated_rental_location_created = True

        # Return the result of the create method
        return res

    def write(self, vals):
        res = super(AitStockLocationResPartner, self).write(vals)
        for record in self:
            if 'dedicated_customer_location' in vals and record.dedicated_customer_location:
                record.dedicated_customer_location_checked()
            if 'dedicated_vendor_location' in vals and record.dedicated_vendor_location:
                record.dedicated_vendor_location_checked()
            if 'dedicated_subcontracting_location' in vals and record.dedicated_subcontracting_location:
                record.dedicated_subcontracting_location_checked()
            if 'dedicated_rental_location' in vals and record.dedicated_rental_location:
                record.dedicated_rental_location_checked()
        return res

    def dedicated_customer_location_checked(self):
        if self.dedicated_customer_location:
            vals = {NAME: self.name}
            self._create_location(vals, 'customer_parent')
            parent_id = self._check_dedicated_location('customer_parent')
            customer_location = self.env['stock.location'].search([
                ('location_id', '=', parent_id),
                ('name', '=', self.name)
            ])
            if customer_location:
                self.property_stock_customer = customer_location[0]
                self.dedicated_customer_location_created = True

    def dedicated_vendor_location_checked(self):
        if self.dedicated_vendor_location:
            vals = {NAME: self.name}
            self._create_location(vals, 'vendor_parent')
            parent_id = self._check_dedicated_location('vendor_parent')
            vendor_location = self.env['stock.location'].search([
                ('location_id', '=', parent_id),
                ('name', '=', self.name)
            ])
            if vendor_location:
                self.property_stock_supplier = vendor_location[0]
                self.dedicated_vendor_location_created = True

    def dedicated_subcontracting_location_checked(self):
        if self.dedicated_subcontracting_location:
            vals = {NAME: self.name}
            self._create_location(vals, 'subcontracting_parent')
            parent_id = self._check_dedicated_location('subcontracting_parent')
            subcontracting_location = self.env['stock.location'].search([
                ('location_id', '=', parent_id),
                ('name', '=', self.name)
            ])
            if subcontracting_location:
                self.property_stock_subcontractor = subcontracting_location[0]
                self.dedicated_subcontracting_location_created = True

    def dedicated_rental_location_checked(self):
        if self.dedicated_rental_location:
            vals = {NAME: self.name}
            self._create_location(vals, 'rental_parent')
            parent_id = self._check_dedicated_location('rental_parent')
            rental_location = self.env['stock.location'].search([
                ('location_id', '=', parent_id),
                ('name', '=', self.name)
            ])
            if rental_location:
                self.property_stock_rental = rental_location[0]
                self.dedicated_rental_location_created = True

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

        # Search for existing warehouse parent
        parent = location_env.sudo().search([('id', '=', parent_id)])
        # Search for existing warehouse with the given name and parent location ID
        warehouse = location_env.sudo().search([(NAME, '=', vals.get(NAME)),
                                                (LOCATION_ID, '=', parent_id)])

        # If warehouse with the same name and parent ID does not exist, create a new one
        if not warehouse:
            location_env.create({
                NAME: vals.get(NAME),
                LOCATION_ID: parent_id,
                'usage': parent.usage,
            })
