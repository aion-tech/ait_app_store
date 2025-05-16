# -*- coding: utf-8 -*-
{
    "name": "Ait Stock Lot Inventory Report",

    "summary": """
    This module allows you to view inventory by lot by providing a location
    list and a date range.
    """,

    "description": """
    The ait_stock_lot_inventory_report module enables the generation of a
    detailed inventory report by specifying a location and date. The report,
    obtained through a wizard, includes information about lots, incoming
    quantities, outgoing quantities, and the difference between them.
    It is based on historical stock movements (stock.move.line) and can be
    easily accessed via a button in the Inventory->Reporting menu. The
    customized view helps in accurately monitoring stock levels for each lot
    at a specific time
    """,

    "author": "Aion Tech s.r.l.",
    "website": "https://aion-tech.it/",

    "license": 'OPL-1',
    'price': 9.99,
    "currency": "EUR",
    "support": "support@aiontech.odoo.com",

    "category": "Inventory Management",
    "version": "18.0.1.0.0",

    "depends": ["base", "stock"],

    "data": [
        "security/ir.model.access.csv",
        "wizard/inventory_wizard_views.xml",
        "views/stock_inventory_detail.xml",
    ],

    'images': ['static/description/thumbnail.png'],

    "installable": True,
    "application": False,
}
