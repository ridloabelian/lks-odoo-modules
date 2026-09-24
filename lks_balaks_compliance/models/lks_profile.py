# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # -------------------------------------------------------------------------
    # LEGALITAS RESMI LEMBAGA KESEJAHTERAAN SOSIAL (LKS)
    # -------------------------------------------------------------------------
    lks_registration_number = fields.Char(
        string="No. Tanda Daftar LKS (Dinas Sosial)",
        help="Nomor Surat Tanda Pendaftaran Lembaga Kesejahteraan Sosial resmi dari Dinas Sosial Provinsi/Kabupaten/Kota.",
    )
    lks_operational_permit = fields.Char(
        string="No. Izin Operasional LKS",
        help="Nomor Izin Penyelenggaraan Pelayanan Sosial (IPPS) / Izin Operasional Panti.",
    )
    lks_permit_expiry_date = fields.Date(
        string="Masa Berlaku Izin Operasional",
    )
    kemenkumham_sk_number = fields.Char(
        string="No. SK Pengesahan Kemenkumham RI",
        help="Nomor Surat Keputusan Menteri Hukum dan HAM RI tentang Pengesahan Badan Hukum Yayasan/Perkumpulan.",
    )
    nib_oss_number = fields.Char(
        string="Nomor Induk Berusaha (NIB OSS)",
        size=13,
    )
    balaks_accreditation_grade = fields.Selection(
        selection=[
            ("A", "Akreditasi A (Sangat Baik)"),
            ("B", "Akreditasi B (Baik)"),
            ("C", "Akreditasi C (Cukup)"),
            ("unaccredited", "Belum Terakreditasi"),
        ],
        string="Peringkat Akreditasi BALAKS",
        default="unaccredited",
    )
    balaks_certificate_number = fields.Char(
        string="Nomor Sertifikat Akreditasi",
        help="Nomor Sertifikat Akreditasi yang diterbitkan oleh Badan Akreditasi Lembaga Kesejahteraan Sosial (BALAKS Kemensos RI).",
    )
    balaks_expiry_date = fields.Date(
        string="Masa Berlaku Akreditasi",
    )

    # -------------------------------------------------------------------------
    # STATISTIK KELEMBAGAAN & RASIO SDM PEKSOS
    # -------------------------------------------------------------------------
    total_active_clients = fields.Integer(
        string="Jumlah Klien PPKS Aktif",
        compute="_compute_lks_stats",
    )
    total_residential_clients = fields.Integer(
        string="Jumlah Klien Residensial (Dalam Panti)",
        compute="_compute_lks_stats",
    )
    total_social_workers = fields.Integer(
        string="Jumlah Pekerja Sosial Bersertifikat",
        compute="_compute_lks_stats",
    )
    social_worker_client_ratio = fields.Char(
        string="Rasio Peksos terhadap Klien",
        compute="_compute_lks_stats",
        help="Rasio jumlah Pekerja Sosial profesional berbanding jumlah klien asuhan (Standar Kemensos: 1 : 15 s/d 1 : 20).",
    )

    def _compute_lks_stats(self):
        partner_obj = self.env["res.partner"]
        user_obj = self.env["res.users"]
        peksos_group = self.env.ref("lks_core.group_lks_social_worker", raise_if_not_found=False)

        for rec in self:
            active_clients = partner_obj.search_count([
                ("is_ppks", "=", True),
                ("service_status", "in", ["intake", "assessment", "active"]),
                ("company_id", "=", rec.id),
            ])
            res_clients = partner_obj.search_count([
                ("is_ppks", "=", True),
                ("residential_status", "=", "in_facility"),
                ("service_status", "in", ["intake", "assessment", "active"]),
                ("company_id", "=", rec.id),
            ])

            sw_count = 0
            if peksos_group:
                sw_count = user_obj.search_count([
                    ("groups_id", "in", [peksos_group.id]),
                    ("company_id", "=", rec.id),
                ])

            rec.total_active_clients = active_clients
            rec.total_residential_clients = res_clients
            rec.total_social_workers = max(1, sw_count) if sw_count else 1
            if sw_count > 0 and active_clients > 0:
                ratio = round(active_clients / sw_count)
                rec.social_worker_client_ratio = f"1 : {ratio}"
            else:
                rec.social_worker_client_ratio = "1 : 0"
