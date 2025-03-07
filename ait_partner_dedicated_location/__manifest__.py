# coding: utf-8
{
    "name": "AIT - Partner Location Auto Create",

    "summary": "AIT - Partner Location Auto Create",

    "description": "AIT - Partner Location Auto Create",

    "author": "Aion Tech s.r.l.",
    "website": "https://aion-tech.it/",

    "license": 'OPL-1',
    "price": 14.99,
    "currency": "EUR",
    "support": "support@aion-tech.odoo.com",

    "category": "Warehouse",
    'version': '16.0.1.0.1',

    'depends': ['stock', 'mrp_subcontracting'],

    'data': [
        'views/res_partner_view.xml',
        'views/res_config_settings.xml',
    ],
    "installable": True,
    "application": False,
}
