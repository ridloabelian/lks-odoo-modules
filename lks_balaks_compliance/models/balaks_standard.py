# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class LksBalaksStandard(models.Model):
    _name = "lks.balaks.standard"
    _description = "6 Standar Nasional Akreditasi LKS (BALAKS Kemensos RI)"
    _order = "sequence asc, code asc"

    code = fields.Char(
        string="Kode Standar",
        size=10,
        required=True,
        index=True,
    )
    name = fields.Char(
        string="Nama Standar Akreditasi",
        required=True,
        index=True,
    )
    sequence = fields.Integer(
        string="Urutan",
        default=10,
    )
    weight = fields.Float(
        string="Bobot Standar (%)",
        required=True,
        default=15.0,
        help="Kontribusi bobot standar ini dalam nilai total 100%.",
    )
    description = fields.Text(
        string="Deskripsi & Ruang Lingkup Standar",
    )
    indicator_ids = fields.One2many(
        comodel_name="lks.balaks.indicator",
        inverse_name="standard_id",
        string="Daftar Indikator Penilaian",
    )
    indicator_count = fields.Integer(
        string="Jumlah Indikator",
        compute="_compute_indicator_count",
    )

    if hasattr(models, "Constraint"):
        _code_uniq = models.Constraint("unique(code)", "Kode Standar Akreditasi harus unik!")
    else:
        _sql_constraints = [
            ("code_uniq", "unique(code)", "Kode Standar Akreditasi harus unik!"),
        ]

    @api.depends("indicator_ids")
    def _compute_indicator_count(self):
        for rec in self:
            rec.indicator_count = len(rec.indicator_ids)

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else (rec.name or "")


class LksBalaksIndicator(models.Model):
    _name = "lks.balaks.indicator"
    _description = "Indikator Penilaian Akreditasi BALAKS Kemensos"
    _order = "standard_id asc, sequence asc, code asc"

    standard_id = fields.Many2one(
        comodel_name="lks.balaks.standard",
        string="Standar Akreditasi",
        required=True,
        ondelete="cascade",
        index=True,
    )
    code = fields.Char(
        string="Kode Indikator",
        size=15,
        required=True,
        index=True,
    )
    name = fields.Char(
        string="Parameter / Indikator",
        required=True,
    )
    sequence = fields.Integer(
        string="Urutan",
        default=10,
    )
    max_score = fields.Float(
        string="Skor Maksimal",
        default=5.0,
        required=True,
        help="Skor maksimal yang dapat diperoleh untuk indikator ini.",
    )
    required_evidence = fields.Text(
        string="Dokumen Bukti Fisik / Eviden yang Dipersyaratkan",
        help="Contoh: SK Kemenkumham, SOP Pelayanan, Buku Induk Klien, STR Pekerja Sosial, Sertifikat APAR",
    )
    verification_guide = fields.Text(
        string="Panduan Verifikasi Asesor / Surveyor",
    )

    if hasattr(models, "Constraint"):
        _code_uniq = models.Constraint("unique(code)", "Kode Indikator Akreditasi harus unik!")
    else:
        _sql_constraints = [
            ("code_uniq", "unique(code)", "Kode Indikator Akreditasi harus unik!"),
        ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else (rec.name or "")
