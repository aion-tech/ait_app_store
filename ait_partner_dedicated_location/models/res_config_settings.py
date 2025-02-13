from odoo import models, fields, api, _

RES_CONFIG_SETTINGS = 'res.config.settings'
STOCK_LOCATION = 'stock.location'
IR_CONFIG_PARAMETER = 'ir.config_parameter'
MODEL = 'partner_location_auto_create'
CUSTOMER = 'customer_parent'
VENDOR = 'vendor_parent'
SUB = 'subcontracting_parent'


class RidixResConfigSettings(models.TransientModel):
    _inherit = RES_CONFIG_SETTINGS
    _description = RES_CONFIG_SETTINGS

    customer_parent = fields.Many2one(comodel_name=STOCK_LOCATION,
                                      string='Customer Location Parent')

    vendor_parent = fields.Many2one(comodel_name=STOCK_LOCATION,
                                    string='Vendor Location Parent')

    subcontracting_parent = fields.Many2one(comodel_name=STOCK_LOCATION,
                                            string='Subcontracting Location Parent')

    # Define a method to retrieve default values for the settings
    @api.model
    def get_values(self):
        # Call the get_values method of the parent class to retrieve default values
        res = super(RidixResConfigSettings, self).get_values()

        # Access the configuration parameter model with sudo to bypass access rights
        config_parameter = self.env[IR_CONFIG_PARAMETER].sudo()

        # Retrieve values for customer, vendor, and subcontracting parents from configuration parameters
        customer_def = int(config_parameter.get_param(
            f'{MODEL}.{CUSTOMER}', default=0))
        vendor_def = int(config_parameter.get_param(
            f'{MODEL}.{VENDOR}', default=0))
        sub_def = int(config_parameter.get_param(f'{MODEL}.{SUB}', default=0))

        # Update the result dictionary with the obtained values
        res.update({
            f'{CUSTOMER}': customer_def,
            f'{VENDOR}': vendor_def,
            f'{SUB}': sub_def,
        })

        # Return the updated result dictionary
        return res

    # Define a method to set values for the settings
    def set_values(self):
        # Call the set_values method of the parent class to perform default value assignments
        res = super(RidixResConfigSettings, self).set_values()

        # Access the configuration parameter model with sudo to bypass access rights
        config_parameter = self.env[IR_CONFIG_PARAMETER].sudo()

        # Set the configuration parameters for customer, vendor, and subcontracting parents
        config_parameter.set_param(
            f'{MODEL}.{CUSTOMER}', self.customer_parent.id or False)
        config_parameter.set_param(
            f'{MODEL}.{VENDOR}', self.vendor_parent.id or False)
        config_parameter.set_param(
            f'{MODEL}.{SUB}', self.subcontracting_parent.id or False)

        # Return the result of the set_values method
        return res
