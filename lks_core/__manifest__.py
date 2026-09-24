# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "LKS & Panti Sosial - Core & Buku Induk",
    "summary": "Master Data 26 Kategori PPKS Kemensos RI, Buku Induk Panti, dan Manajemen Residensial Asrama",
    "version": "19.0.1.0.0",
    "category": "Social Welfare/Non-Profit",
    "author": "Lembaga Kesejahteraan Sosial (LKS) Indonesia, Odoo Community Association (OCA)",
    "website": "https://github.com/lks-odoo-modules",
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "base",
        "mail",
        "npo_partner_id",
    ],
    "data": [
        "security/lks_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ppks_category_data.xml",
        "views/facility_management_views.xml",
        "views/res_partner_views.xml",
        "views/ppks_category_views.xml",
        "views/buku_induk_register_views.xml",
        "views/lks_menus.xml",
        "report/ppks_reports.xml",
        "report/ppks_card_template.xml",
        "report/buku_induk_template.xml",
    ],
    "images": [
        "static/description/icon.png",
    ],
}
