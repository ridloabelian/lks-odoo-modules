# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class LksEducationRecord(models.Model):
    _name = "lks.education.record"
    _description = "Rekam Perkembangan Pendidikan Klien PPKS"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "academic_year desc, id desc"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Nama Klien PPKS",
        required=True,
        domain="[('is_ppks', '=', True)]",
        index=True,
        tracking=True,
    )
    registration_number = fields.Char(
        string="No. Induk PPKS",
        related="partner_id.registration_number",
        store=True,
        readonly=True,
    )
    level = fields.Selection(
        selection=[
            ("paud", "PAUD / Kelompok Bermain"),
            ("tk", "TK / RA"),
            ("sd", "SD / MI / Paket A"),
            ("smp", "SMP / MTs / Paket B"),
            ("sma", "SMA / MA / Paket C"),
            ("smk", "SMK"),
            ("slb", "SLB (Sekolah Luar Biasa)"),
            ("pesantren", "Pondok Pesantren"),
            ("higher", "Perguruan Tinggi (Diploma/Sarjana)"),
            ("vocational", "Pelatihan Kerja / Vokasional BLK"),
            ("none", "Belum / Tidak Bersekolah"),
        ],
        string="Jenjang Pendidikan",
        default="sd",
        required=True,
        tracking=True,
    )
    school_name = fields.Char(
        string="Nama Sekolah / Lembaga",
        required=True,
        tracking=True,
        help="Contoh: SDN 1 Merdeka, SMPN 3 Cimahi, SLB Negeri A Cicendo",
    )
    school_address = fields.Text(
        string="Alamat Sekolah",
    )
    nisn = fields.Char(
        string="NISN",
        size=10,
        help="Nomor Induk Siswa Nasional (10 digit resmi Kemendikbudristek/Kemenag).",
    )
    current_grade = fields.Char(
        string="Tingkat / Kelas Saat Ini",
        help="Contoh: Kelas 4, Kelas 8, Tingkat 2, Semester 3",
        tracking=True,
    )
    academic_year = fields.Char(
        string="Tahun Ajaran",
        default="2025/2026",
        required=True,
        tracking=True,
    )
    major = fields.Char(
        string="Jurusan / Program Keahlian",
        help="Untuk jenjang SMK/Perguruan Tinggi/Pelatihan Kerja (contoh: Rekayasa Perangkat Lunak, Tata Boga, Otomotif)",
    )
    status = fields.Selection(
        selection=[
            ("enrolled", "Aktif Bersekolah"),
            ("graduated", "Lulus"),
            ("dropped_out", "Putus Sekolah / Berhenti"),
            ("transferred", "Pindah Sekolah"),
        ],
        string="Status Pendidikan",
        default="enrolled",
        required=True,
        tracking=True,
    )
    funding_type = fields.Selection(
        selection=[
            ("kip", "KIP / PIP Kemendikbudristek"),
            ("bos", "Gratis / BOS Pemerintah"),
            ("foundation", "Beasiswa Subsidi Panti / Yayasan"),
            ("foster_parent", "Orang Tua Asuh / Donatur Khusus"),
            ("self", "Mandiri / Keluarga"),
        ],
        string="Sumber Pembiayaan Pendidikan",
        default="foundation",
        required=True,
        tracking=True,
    )
    foster_parent_name = fields.Char(
        string="Nama Donatur / Orang Tua Asuh",
    )
    # Ijazah & Kelulusan
    diploma_number = fields.Char(
        string="Nomor Seri Ijazah",
        tracking=True,
    )
    diploma_date = fields.Date(
        string="Tanggal Kelulusan / Ijazah",
    )
    diploma_file = fields.Binary(
        string="Scan Ijazah / Sertifikat Kelulusan",
        attachment=True,
    )
    diploma_filename = fields.Char(
        string="Nama File Ijazah",
    )
    # Evaluasi Rapor
    report_card_ids = fields.One2many(
        comodel_name="lks.education.report_card",
        inverse_name="education_id",
        string="Riwayat Evaluasi Rapor Semester",
    )
    report_card_count = fields.Integer(
        string="Jumlah Rapor",
        compute="_compute_report_card_count",
    )
    notes = fields.Text(
        string="Catatan Perkembangan Akademik",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.depends("report_card_ids")
    def _compute_report_card_count(self):
        for rec in self:
            rec.report_card_count = len(rec.report_card_ids)

    @api.depends("partner_id.name", "level", "school_name")
    def _compute_display_name(self):
        for rec in self:
            client = rec.partner_id.name if rec.partner_id else ""
            rec.display_name = f"{client} - {rec.school_name} ({dict(rec._fields['level'].selection).get(rec.level, '')})"


class LksEducationReportCard(models.Model):
    _name = "lks.education.report_card"
    _description = "Evaluasi Nilai Rapor Semester PPKS"
    _order = "academic_year desc, semester desc"

    education_id = fields.Many2one(
        comodel_name="lks.education.record",
        string="Data Sekolah",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Klien PPKS",
        related="education_id.partner_id",
        store=True,
        readonly=True,
    )
    academic_year = fields.Char(
        string="Tahun Pelajaran",
        required=True,
        default="2025/2026",
    )
    semester = fields.Selection(
        selection=[
            ("odd", "Semester 1 (Ganjil)"),
            ("even", "Semester 2 (Genap)"),
        ],
        string="Semester",
        default="odd",
        required=True,
    )
    grade_level = fields.Char(
        string="Kelas",
        help="Contoh: Kelas VII-B, Kelas 5 SD",
    )
    average_score = fields.Float(
        string="Nilai Rata-rata Rapor",
        help="Nilai rata-rata rapor skala 0 - 100",
    )
    rank = fields.Integer(
        string="Peringkat Kelas",
        help="Peringkat/ranking siswa di kelas",
    )
    total_students = fields.Integer(
        string="Dari Total Siswa",
        default=30,
    )
    behavior_grade = fields.Selection(
        selection=[
            ("A", "Sangat Baik (A)"),
            ("B", "Baik (B)"),
            ("C", "Cukup (C)"),
            ("D", "Perlu Bimbingan (D)"),
        ],
        string="Sikap & Perilaku",
        default="B",
    )
    achievements = fields.Text(
        string="Prestasi Akademik / Non-Akademik",
        help="Juara kelas, perlombaan seni, olahraga, sains, dll.",
    )
    extracurricular = fields.Char(
        string="Kegiatan Ekstrakurikuler",
        help="Contoh: Pramuka, PMR, Futsal, Seni Musik, Tahfidz",
    )
    homeroom_notes = fields.Text(
        string="Catatan Wali Kelas / Evaluasi Peksos",
    )
    report_file = fields.Binary(
        string="Scan Buku Rapor",
        attachment=True,
    )
    report_filename = fields.Char(
        string="Nama File Rapor",
    )
