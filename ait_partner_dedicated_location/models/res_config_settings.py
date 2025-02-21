from odoo import models, fields, api

RES_CONFIG = 'res.config.settings'
STOCK_LOCATION = 'stock.location'
IR_CONFIG_PARAMETER = 'ir.config_parameter'
MODEL = 'ait_partner_dedicated_location'
CUSTOMER = 'customer_parent'
VENDOR = 'vendor_parent'
SUB = 'subcontracting_parent'
RENTAL = 'rental_parent'


class ResConfig(models.TransientModel):
    _inherit = RES_CONFIG

    customer_parent = fields.Many2one(STOCK_LOCATION, string='Customer Location Parent',
                                      compute="_compute_customer_parent", inverse="_set_customer_parent", store=False)

    vendor_parent = fields.Many2one(STOCK_LOCATION, string='Vendor Location Parent',
                                    compute="_compute_vendor_parent", inverse="_set_vendor_parent", store=False)

    subcontracting_parent = fields.Many2one(STOCK_LOCATION, string='Subcontracting Location Parent',
                                            compute="_compute_subcontracting_parent", inverse="_set_subcontracting_parent", store=False)

    rental_parent = fields.Many2one(comodel_name=STOCK_LOCATION, string='Rental Location Parent',
                                    compute="_compute_rental_parent", inverse="_set_rental_parent", store=False)

    # --- COMPUTE METHODS ---
    @api.depends()
    def _compute_customer_parent(self):
        """ Recupera il valore Many2one dal config_parameter """
        for record in self:
            customer_id = int(self.env[IR_CONFIG_PARAMETER].sudo().get_param(f'{MODEL}.{CUSTOMER}', default=0))
            record.customer_parent = self.env[STOCK_LOCATION].browse(customer_id) if customer_id else False

    @api.depends()
    def _compute_vendor_parent(self):
        for record in self:
            vendor_id = int(self.env[IR_CONFIG_PARAMETER].sudo().get_param(f'{MODEL}.{VENDOR}', default=0))
            record.vendor_parent = self.env[STOCK_LOCATION].browse(vendor_id) if vendor_id else False

    @api.depends()
    def _compute_subcontracting_parent(self):
        for record in self:
            sub_id = int(self.env[IR_CONFIG_PARAMETER].sudo().get_param(f'{MODEL}.{SUB}', default=0))
            record.subcontracting_parent = self.env[STOCK_LOCATION].browse(sub_id) if sub_id else False

    @api.depends()
    def _compute_rental_parent(self):
        for record in self:
            rental_id = int(self.env[IR_CONFIG_PARAMETER].sudo().get_param(f'{MODEL}.{RENTAL}', default=0))
            record.rental_parent = self.env[STOCK_LOCATION].browse(rental_id) if rental_id else False

    # --- SET METHODS ---
    def _set_customer_parent(self):
        """ Salva il valore Many2one nel config_parameter """
        for record in self:
            self.env[IR_CONFIG_PARAMETER].sudo().set_param(f'{MODEL}.{CUSTOMER}', record.customer_parent.id or 0)

    def _set_vendor_parent(self):
        for record in self:
            self.env[IR_CONFIG_PARAMETER].sudo().set_param(f'{MODEL}.{VENDOR}', record.vendor_parent.id or 0)

    def _set_subcontracting_parent(self):
        for record in self:
            self.env[IR_CONFIG_PARAMETER].sudo().set_param(f'{MODEL}.{SUB}', record.subcontracting_parent.id or 0)

    def _set_rental_parent(self):
        for record in self:
            self.env[IR_CONFIG_PARAMETER].sudo().set_param(f'{MODEL}.{RENTAL}', record.rental_parent.id or 0)

    # --- OVERRIDE GET/SET VALUES ---
    @api.model
    def get_values(self):
        """ Recupera i valori dal config_parameter per l'interfaccia settings """
        res = super().get_values()
        config_parameter = self.env[IR_CONFIG_PARAMETER].sudo()

        res.update({
            CUSTOMER: int(config_parameter.get_param(f'{MODEL}.{CUSTOMER}', default=0)) or False,
            VENDOR: int(config_parameter.get_param(f'{MODEL}.{VENDOR}', default=0)) or False,
            SUB: int(config_parameter.get_param(f'{MODEL}.{SUB}', default=0)) or False,
            RENTAL: int(config_parameter.get_param(f'{MODEL}.{RENTAL}', default=0)) or False,
        })
        return res

    def set_values(self):
        """ Salva i valori nel config_parameter """
        super().set_values()
        config_parameter = self.env[IR_CONFIG_PARAMETER].sudo()

        config_parameter.set_param(f'{MODEL}.{CUSTOMER}', self.customer_parent.id or 0)
        config_parameter.set_param(f'{MODEL}.{VENDOR}', self.vendor_parent.id or 0)
        config_parameter.set_param(f'{MODEL}.{SUB}', self.subcontracting_parent.id or 0)
        config_parameter.set_param(f'{MODEL}.{RENTAL}', self.rental_parent.id or 0)
