# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class LksPpksCategory(models.Model):
    _name = "lks.ppks.category"
    _description = "26 Kategori Pemerlu Pelayanan Kesejahteraan Sosial (PPKS) Kemensos"
    _order = "sequence asc, code asc"

    code = fields.Char(
        string="Kode PPKS",
        size=10,
        required=True,
        index=True,
        help="Kode singkatan resmi PPKS Kemensos (contoh: ABT, AT, ABH, LUT, DIS-FISIK)",
    )
    name = fields.Char(
        string="Nama Kategori PPKS",
        required=True,
        index=True,
        help="Nama resmi kategori pemerlu pelayanan kesejahteraan sosial sesuai Permensos",
    )
    cluster = fields.Selection(
        selection=[
            ("anak", "Kluster Anak & Remaja"),
            ("lansia", "Kluster Lanjut Usia"),
            ("disabilitas", "Kluster Penyandang Disabilitas"),
            ("tunasosial", "Kluster Tuna Sosial & Napza"),
            ("korban", "Kluster Korban Kekerasan, TPPO & Bencana"),
            ("keluarga", "Kluster Fakir Miskin & Keluarga Rentan"),
        ],
        string="Kluster PPKS",
        required=True,
        index=True,
        default="anak",
    )
    sequence = fields.Integer(
        string="Urutan",
        default=10,
    )
    description = fields.Text(
        string="Definisi & Kriteria Kemensos",
        help="Deskripsi kriteria dan batasan kategori sesuai pedoman teknis Kemensos RI.",
    )
    legal_basis = fields.Char(
        string="Dasar Regulasi",
        default="Permensos No. 08 Tahun 2012 / UU No. 11 Tahun 2009",
    )
    age_group_target = fields.Selection(
        selection=[
            ("all", "Semua Usia"),
            ("balita", "Balita (0 - 4 Tahun)"),
            ("anak", "Anak (5 - 17 Tahun)"),
            ("dewasa", "Dewasa (18 - 59 Tahun)"),
            ("lansia", "Lanjut Usia (>= 60 Tahun)"),
        ],
        string="Sasaran Usia",
        default="all",
        required=True,
    )
    target_services = fields.Char(
        string="Standar Pelayanan Minimal (SPM)",
        help="Bentuk layanan yang wajib diberikan (contoh: Permakanan, Asuhan Pengganti, Rehabilitasi Sosial, Advokasi)",
    )
    active = fields.Boolean(
        string="Aktif",
        default=True,
    )
    client_count = fields.Integer(
        string="Jumlah Klien Terdaftar",
        compute="_compute_client_count",
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Kode Kategori PPKS harus unik!"),
    ]

    def _compute_client_count(self):
        partner_obj = self.env["res.partner"]
        for rec in self:
            rec.client_count = partner_obj.search_count([
                ("is_ppks", "=", True),
                ("ppks_category_id", "=", rec.id),
            ])

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else (rec.name or "")
