# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Akuntansi Nonlaba & Yayasan Sosial (ISAK 35)",
    "summary": "Bagan Akun Standar (COA) dan 4 Laporan Keuangan Wajib Entitas Nonlaba berbasis ISAK 35 IAI",
    "version": "20.0.1.0.0",
    "category": "Accounting/Localizations",
    "author": "Lembaga Kesejahteraan Sosial (LKS) Indonesia, Odoo Community Association (OCA)",
    "website": "https://github.com/lks-odoo-modules",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": [
        "account",
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_chart_template_data.xml",
        "views/account_account_views.xml",
        "views/account_move_views.xml",
        "views/isak35_report_wizard_views.xml",
        "views/isak35_menus.xml",
        "report/isak35_reports.xml",
        "report/isak35_financial_report_template.xml",
    ],
    "images": [
        "static/description/icon.png",
    ],
}
