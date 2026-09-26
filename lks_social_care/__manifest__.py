# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "LKS & Panti Sosial - Manajemen Asuhan & Perkembangan PPKS (Case Management)",
    "summary": "Case Management PPKS, Monitoring Pendidikan & Rapor, Rekam Medis Panti, Rencana Intervensi & Terminasi/Reuni",
    "version": "18.0.1.0.0",
    "category": "Social Welfare/Non-Profit",
    "author": "Lembaga Kesejahteraan Sosial (LKS) Indonesia, Odoo Community Association (OCA)",
    "website": "https://github.com/lks-odoo-modules",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": [
        "lks_core",
        "npo_assessment",
        "npo_disbursement_base",
    ],
    "data": [
        "security/lks_social_care_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/education_record_views.xml",
        "views/medical_record_views.xml",
        "views/case_management_views.xml",
        "views/res_partner_views.xml",
        "views/social_care_menus.xml",
        "report/social_care_reports.xml",
        "report/case_plan_template.xml",
        "report/medical_record_template.xml",
    ],
    "images": [
        "static/description/icon.png",
    ],
}
