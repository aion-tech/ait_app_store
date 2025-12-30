{
    "name": "attachment_utils",
    "summary": "",
    "description": "",
    "author": "Aion Tech Srl",
    "website": "https://aion-tech.it/",
    "license": "LGPL-1",
    # https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    "category": "Uncategorized",
    "version": "16.0.1.0.1",
    "depends": [
        "base",
        # "web_notify",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_attachment_rule_views.xml",
    ],
}
