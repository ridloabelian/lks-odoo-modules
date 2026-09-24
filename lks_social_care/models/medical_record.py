# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class LksMedicalRecord(models.Model):
    _name = "lks.medical.record"
    _description = "Rekam Medis & Profil Kesehatan Dasar PPKS Panti"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

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
    gender = fields.Selection(
        related="partner_id.gender",
        string="Jenis Kelamin",
        readonly=True,
    )
    age = fields.Integer(
        related="partner_id.age",
        string="Usia (Tahun)",
        readonly=True,
    )
    # Golongan Darah & Alergi
    blood_type = fields.Selection(
        selection=[
            ("A", "A"),
            ("B", "B"),
            ("AB", "AB"),
            ("O", "O"),
            ("unknown", "Belum Diketahui"),
        ],
        string="Golongan Darah",
        default="unknown",
        tracking=True,
    )
    rhesus = fields.Selection(
        selection=[
            ("positive", "Rh Positif (+)"),
            ("negative", "Rh Negatif (-)"),
            ("unknown", "Belum Diketahui"),
        ],
        string="Faktor Rhesus",
        default="unknown",
    )
    allergies = fields.Text(
        string="Riwayat Alergi (Makanan, Obat, Suhu)",
        help="Contoh: Alergi antibiotik Amoxicillin, Alergi udang/seafood, Alergi dingin",
        tracking=True,
    )
    chronic_diseases = fields.Text(
        string="Riwayat Penyakit Kronis / Bawaan",
        help="Contoh: Asma bronkial, Epilepsi, Penyakit Jantung Bawaan, Diabetes Melitus, Hipertensi, TBC",
        tracking=True,
    )
    disability_special_needs = fields.Text(
        string="Kebutuhan Khusus / Alat Bantu Medis",
        help="Contoh: Memerlukan kursi roda, kacamata minus 4.0, alat bantu dengar (ABD), kateter urin",
    )
    dietary_needs = fields.Char(
        string="Diet Khusus / Pantangan Makanan",
        help="Diet rendah garam untuk lansia, diet bebas gluten, dll.",
    )
    # Penjamin Kesehatan
    bpjs_type = fields.Selection(
        selection=[
            ("pbi", "BPJS Kesehatan PBI APBN / APBD (KIS Gratis)"),
            ("non_pbi", "BPJS Mandiri / Peserta Pekerja"),
            ("foundation", "Ditanggung Penuh Subsidi Yayasan / Panti"),
            ("none", "Belum Memiliki Jaminan Kesehatan"),
        ],
        string="Jaminan Kesehatan",
        default="pbi",
        tracking=True,
    )
    bpjs_number = fields.Char(
        string="Nomor Kartu KIS / BPJS",
        size=16,
        tracking=True,
    )
    bpjs_faskes = fields.Char(
        string="Fasilitas Kesehatan Tingkat 1 (Faskes 1)",
        help="Puskesmas atau klinik pratama terdaftar di kartu BPJS.",
    )
    # Relasi Imunisasi & Kunjungan
    immunization_ids = fields.One2many(
        comodel_name="lks.medical.immunization",
        inverse_name="medical_id",
        string="Riwayat Imunisasi & Vaksinasi",
    )
    visit_ids = fields.One2many(
        comodel_name="lks.medical.visit",
        inverse_name="medical_id",
        string="Riwayat Pemeriksaan & Berobat",
    )
    visit_count = fields.Integer(
        string="Jumlah Kunjungan Berobat",
        compute="_compute_visit_count",
    )
    # Parameter Fisik Terkini
    latest_weight = fields.Float(
        string="Berat Badan Terkini (kg)",
        compute="_compute_latest_vitals",
        store=True,
    )
    latest_height = fields.Float(
        string="Tinggi Badan Terkini (cm)",
        compute="_compute_latest_vitals",
        store=True,
    )
    latest_bmi = fields.Float(
        string="Indeks Massa Tubuh (IMT)",
        compute="_compute_latest_vitals",
        store=True,
    )
    latest_bmi_status = fields.Char(
        string="Status Gizi (IMT)",
        compute="_compute_latest_vitals",
        store=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        default=lambda self: self.env.company,
        required=True,
    )

    if hasattr(models, "Constraint"):
        _partner_uniq = models.Constraint("unique(partner_id)", "Rekam Medis untuk klien PPKS ini sudah ada!")
    else:
        _sql_constraints = [
            ("partner_uniq", "unique(partner_id)", "Rekam Medis untuk klien PPKS ini sudah ada!"),
        ]

    @api.depends("visit_ids")
    def _compute_visit_count(self):
        for rec in self:
            rec.visit_count = len(rec.visit_ids)

    @api.depends("visit_ids.weight", "visit_ids.height", "visit_ids.date")
    def _compute_latest_vitals(self):
        for rec in self:
            latest_visit = rec.visit_ids.sorted(key=lambda v: (v.date or fields.Date.min, v.id), reverse=True)
            if latest_visit and latest_visit[0].weight and latest_visit[0].height:
                w = latest_visit[0].weight
                h = latest_visit[0].height / 100.0  # konversi ke meter
                bmi = round(w / (h * h), 1) if h > 0 else 0.0
                rec.latest_weight = w
                rec.latest_height = latest_visit[0].height
                rec.latest_bmi = bmi
                if bmi < 17.0:
                    rec.latest_bmi_status = "Kurus (Gizi Kurang)"
                elif 17.0 <= bmi < 18.5:
                    rec.latest_bmi_status = "Gizi Cukup Ringan"
                elif 18.5 <= bmi <= 25.0:
                    rec.latest_bmi_status = "Normal / Ideal"
                elif 25.0 < bmi <= 27.0:
                    rec.latest_bmi_status = "Kelebihan Berat Badan"
                else:
                    rec.latest_bmi_status = "Obesitas"
            else:
                rec.latest_weight = 0.0
                rec.latest_height = 0.0
                rec.latest_bmi = 0.0
                rec.latest_bmi_status = "Belum Ada Pengukuran"

    @api.depends("partner_id.name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"Rekam Medis - {rec.partner_id.name or ''}"


class LksMedicalImmunization(models.Model):
    _name = "lks.medical.immunization"
    _description = "Riwayat Imunisasi PPKS"
    _order = "vaccine_date desc, id desc"

    medical_id = fields.Many2one(
        comodel_name="lks.medical.record",
        string="Rekam Medis",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Klien PPKS",
        related="medical_id.partner_id",
        store=True,
        readonly=True,
    )
    vaccine_name = fields.Selection(
        selection=[
            ("bcg", "BCG (TBC)"),
            ("hepatitis_b", "Hepatitis B"),
            ("polio", "Polio (OPV / IPV)"),
            ("dpt_hb_hib", "DPT-HB-Hib (Pentavalen)"),
            ("pcv", "PCV (Pneumokokus)"),
            ("rotavirus", "Rotavirus"),
            ("campak_rubella", "Campak / MR / MMR"),
            ("dt", "DT / Td (Booster SD)"),
            ("covid", "COVID-19"),
            ("influenza", "Influenza (Geriatri/Lansia)"),
            ("other", "Vaksin / Imunisasi Lainnya"),
        ],
        string="Nama Vaksin / Imunisasi",
        required=True,
    )
    vaccine_date = fields.Date(
        string="Tanggal Diberikan",
        default=fields.Date.context_today,
        required=True,
    )
    dose = fields.Selection(
        selection=[
            ("0", "Dosis 0 (Kelahiran)"),
            ("1", "Dosis 1"),
            ("2", "Dosis 2"),
            ("3", "Dosis 3"),
            ("4", "Dosis 4"),
            ("booster", "Booster / Penguat"),
        ],
        string="Dosis Ke-",
        default="1",
        required=True,
    )
    administered_at = fields.Char(
        string="Tempat / Faskes Pemberian",
        help="Puskesmas, Posyandu, Rumah Sakit",
    )
    batch_number = fields.Char(
        string="No. Batch Vaksin",
    )
    notes = fields.Char(
        string="Keterangan / KIPI",
        help="Reaksi pasca imunisasi jika ada (demam ringan, dll.)",
    )


class LksMedicalVisit(models.Model):
    _name = "lks.medical.visit"
    _description = "Log Kunjungan Medis & Pemeriksaan Kesehatan PPKS"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    medical_id = fields.Many2one(
        comodel_name="lks.medical.record",
        string="Rekam Medis Klien",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Klien PPKS",
        related="medical_id.partner_id",
        store=True,
        readonly=True,
    )
    date = fields.Date(
        string="Tanggal Berobat / Periksa",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    healthcare_facility = fields.Selection(
        selection=[
            ("panti_clinic", "Ruang Kesehatan / Medis Panti"),
            ("puskesmas", "Puskesmas"),
            ("hospital", "RSUD / Rumah Sakit"),
            ("posyandu", "Posyandu / Posbindu Lansia"),
            ("private_clinic", "Klinik / Dokter Praktik Mandiri"),
            ("other", "Lainnya"),
        ],
        string="Fasilitas Kesehatan",
        default="puskesmas",
        required=True,
        tracking=True,
    )
    facility_name = fields.Char(
        string="Nama Faskes / Rumah Sakit",
        help="Contoh: Puskesmas Dago, RSUD Hasan Sadikin",
    )
    medical_staff = fields.Char(
        string="Dokter / Tenaga Medis Pemeriksa",
    )
    # Tanda Vital & Fisik
    weight = fields.Float(
        string="Berat Badan (kg)",
        tracking=True,
    )
    height = fields.Float(
        string="Tinggi Badan (cm)",
        tracking=True,
    )
    bmi = fields.Float(
        string="IMT",
        compute="_compute_bmi",
        store=True,
    )
    blood_pressure = fields.Char(
        string="Tekanan Darah (mmHg)",
        help="Contoh: 120/80 mmHg",
    )
    body_temperature = fields.Float(
        string="Suhu Tubuh (°C)",
        default=36.5,
    )
    # Keluhan & Diagnosis
    complaint = fields.Text(
        string="Keluhan Utama / Gejala",
        required=True,
    )
    diagnosis = fields.Text(
        string="Diagnosis Medis",
        required=True,
        tracking=True,
    )
    treatment = fields.Text(
        string="Tindakan Medis & Penanganan",
    )
    prescription = fields.Text(
        string="Resep & Aturan Minum Obat",
    )
    # Pembiayaan
    cost = fields.Monetary(
        string="Biaya Berobat / Obat",
        currency_field="currency_id",
    )
    cost_coverage = fields.Selection(
        selection=[
            ("bpjs", "Gratis (BPJS PBI / KIS)"),
            ("foundation", "Ditanggung Penuh Yayasan/Panti"),
            ("donor", "Donatur Peduli Khusus"),
            ("self", "Keluarga Klien"),
        ],
        string="Sumber Pembayaran",
        default="bpjs",
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Mata Uang",
        default=lambda self: self.env.company.currency_id,
    )
    follow_up_date = fields.Date(
        string="Jadwal Kontrol Ulang",
    )
    notes = fields.Text(
        string="Catatan Dokter / Perawat",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        related="medical_id.company_id",
        store=True,
        readonly=True,
    )

    @api.depends("weight", "height")
    def _compute_bmi(self):
        for rec in self:
            if rec.weight and rec.height:
                h_meter = rec.height / 100.0
                rec.bmi = round(rec.weight / (h_meter * h_meter), 1) if h_meter > 0 else 0.0
            else:
                rec.bmi = 0.0
