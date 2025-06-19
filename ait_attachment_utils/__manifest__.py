{
    "name": "attachment_utils",
    "summary": "",
    "description": "",
    "author": "Aion Tech Srl",
    "website": "https://aion-tech.it/",
    # https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    "category": "Uncategorized",
    "version": "17.0.1.0.0",
    "depends": [
        "base", "mail"
        # "web_notify",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_attachment_rule_views.xml",
        "views/assets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ait_attachment_utils/static/src/core/attachment_upload_service_patch.js",
        ],
    },
}
