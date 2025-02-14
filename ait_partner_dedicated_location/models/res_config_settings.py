from odoo import models, fields, api, _

RES_CONFIG = 'res.config'  # Cambiato da 'res.config.settings' a 'res.config' in Odoo 17+
STOCK_LOCATION = 'stock.location'
IR_CONFIG_PARAMETER = 'ir.config_parameter'
MODEL = 'partner_location_auto_create'
CUSTOMER = 'customer_parent'
VENDOR = 'vendor_parent'
SUB = 'subcontracting_parent'


class RidixResConfig(models.TransientModel):
    _inherit = RES_CONFIG
    _description = RES_CONFIG

    customer_parent = fields.Many2one(comodel_name=STOCK_LOCATION,
                                      string='Customer Location Parent')

    vendor_parent = fields.Many2one(comodel_name=STOCK_LOCATION,
                                    string='Vendor Location Parent')

    subcontracting_parent = fields.Many2one(comodel_name=STOCK_LOCATION,
                                            string='Subcontracting Location Parent')

    @api.model
    def get_values(self):
        res = super().get_values()
        config_parameter = self.env[IR_CONFIG_PARAMETER].sudo()

        customer_def = int(config_parameter.get_param(f'{MODEL}.{CUSTOMER}', default=0))
        vendor_def = int(config_parameter.get_param(f'{MODEL}.{VENDOR}', default=0))
        sub_def = int(config_parameter.get_param(f'{MODEL}.{SUB}', default=0))

        res.update({
            CUSTOMER: customer_def,
            VENDOR: vendor_def,
            SUB: sub_def,
        })
        return res

    def set_values(self):
        super().set_values()
        config_parameter = self.env[IR_CONFIG_PARAMETER].sudo()

        config_parameter.set_param(f'{MODEL}.{CUSTOMER}', self.customer_parent.id or False)
        config_parameter.set_param(f'{MODEL}.{VENDOR}', self.vendor_parent.id or False)
        config_parameter.set_param(f'{MODEL}.{SUB}', self.subcontracting_parent.id or False)
