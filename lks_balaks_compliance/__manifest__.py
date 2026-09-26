# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Kepatuhan Akreditasi LKS & Ekspor SIKS-NG Kemensos",
    "summary": "Audit Kesiapan 6 Standar Nasional BALAKS Kemensos, Profil Lembaga, dan Ekspor Data Binaan SIKS-NG / Dinsos",
    "version": "20.0.1.0.0",
    "category": "Social Welfare/Non-Profit",
    "author": "Lembaga Kesejahteraan Sosial (LKS) Indonesia, Odoo Community Association (OCA)",
    "website": "https://github.com/lks-odoo-modules",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": [
        "lks_core",
        "lks_social_care",
        "l10n_id_nonprofit_isak35",
    ],
    "data": [
        "security/lks_balaks_security.xml",
        "security/ir.model.access.csv",
        "data/balaks_standard_data.xml",
        "views/balaks_standard_views.xml",
        "views/balaks_audit_views.xml",
        "views/lks_profile_views.xml",
        "views/siksng_export_wizard_views.xml",
        "views/balaks_menus.xml",
        "report/balaks_reports.xml",
        "report/balaks_audit_report_template.xml",
    ],
    "images": [
        "static/description/icon.png",
    ],
}
