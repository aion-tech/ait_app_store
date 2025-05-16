# -*- coding: utf-8 -*-

from odoo import models, fields


class StockLotHistory(models.TransientModel):
    _name = "stock.inventory.detail"
    _description = "Detailed inventory by lot"

    name = fields.Char(string="Name")
    location_id = fields.Many2one(comodel_name="stock.location", string="Location")
    product_id = fields.Many2one(comodel_name="product.template", string="Product")
    lot_id = fields.Many2one(comodel_name="stock.lot", string="Lot")
    incoming_qty = fields.Float(string="Incoming quantity")
    outgoing_qty = fields.Float(string="Outgoing quantity")
    net_qty = fields.Float(string="Net quantity")
