# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LksCasePlan(models.Model):
    _name = "lks.case.plan"
    _description = "Rencana Intervensi Layanan Individual PPKS (Case Plan)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "plan_date desc, id desc"

    name = fields.Char(
        string="No. Rencana Intervensi",
        required=True,
        copy=False,
        readonly=True,
        default="/",
        tracking=True,
    )
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
    ppks_category_id = fields.Many2one(
        comodel_name="lks.ppks.category",
        string="Kategori PPKS",
        related="partner_id.ppks_category_id",
        store=True,
        readonly=True,
    )
    social_worker_id = fields.Many2one(
        comodel_name="res.users",
        string="Pekerja Sosial Pendamping (Peksos)",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    plan_date = fields.Date(
        string="Tanggal Rencana Intervensi",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    target_completion_date = fields.Date(
        string="Target Waktu Penyelesaian",
        tracking=True,
    )
    review_period = fields.Selection(
        selection=[
            ("1_month", "Evaluasi Setiap 1 Bulan"),
            ("3_months", "Evaluasi Setiap 3 Bulan (Triwulan)"),
            ("6_months", "Evaluasi Setiap 6 Bulan (Semester)"),
            ("1_year", "Evaluasi Tahunan"),
        ],
        string="Siklus Review Evaluasi",
        default="3_months",
        required=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft Rancangan"),
            ("approved", "Disetujui Pimpinan"),
            ("ongoing", "Dalam Pelaksanaan Intervensi"),
            ("evaluated", "Evaluasi Selesai"),
            ("closed", "Selesai / Ditutup"),
            ("cancel", "Dibatalkan"),
        ],
        string="Status Rencana",
        default="draft",
        tracking=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # ANALISIS ASESMEN & SASARAN LAYANAN
    # -------------------------------------------------------------------------
    problem_identification = fields.Text(
        string="Identifikasi Masalah & Kerentanan",
        required=True,
        help="Permasalahan utama yang dihadapi klien (penelantaran, putus sekolah, disfungsi keluarga, trauma psikologis, dll.).",
    )
    client_strengths = fields.Text(
        string="Potensi & Kekuatan Klien",
        help="Bakat, minat, motivasi belajar, dukungan kerabat yang dapat dioptimalkan.",
    )
    short_term_goals = fields.Text(
        string="Tujuan Jangka Pendek (1 - 3 Bulan)",
        required=True,
        help="Adaptasi asrama, pemulihan kesehatan fisik dasar, penempatan sekolah baru.",
    )
    long_term_goals = fields.Text(
        string="Tujuan Jangka Panjang (6 - 12 Bulan / Terminasi)",
        required=True,
        help="Penyelesaian jenjang pendidikan, kesiapan kemandirian, reunifikasi ke keluarga.",
    )

    # -------------------------------------------------------------------------
    # 4 PILAR STRATEGI INTERVENSI SOSIAL KEMENSOS
    # -------------------------------------------------------------------------
    physical_guidance = fields.Text(
        string="1. Bimbingan Fisik & Kesehatan",
        help="Pemenuhan gizi seimbang, kebersihan diri, olahraga, imunisasi dan pengobatan rutin.",
    )
    mental_spiritual_guidance = fields.Text(
        string="2. Bimbingan Mental & Spiritual",
        help="Pembinaan ibadah keagamaan, penanaman nilai budi pekerti, konseling spiritual.",
    )
    social_guidance = fields.Text(
        string="3. Bimbingan Sosial & Psikologis",
        help="Konseling individu, terapi perilaku, bimbingan dinamika kelompok, penyesuaian sosial.",
    )
    vocational_training = fields.Text(
        string="4. Pelatihan Vokasional & Minat Bakat",
        help="Kursus keterampilan kerja, komputer, menjahit, seni kriya, atau kursus wirausaha mandiri.",
    )

    # -------------------------------------------------------------------------
    # EVALUASI & CAPAIAN BERKALA
    # -------------------------------------------------------------------------
    progress_evaluation = fields.Text(
        string="Catatan Perkembangan & Evaluasi Capaian",
        help="Catatan kemajuan aktual yang dicapai klien selama periode intervensi.",
    )
    success_indicators = fields.Text(
        string="Indikator Keberhasilan Intervensi",
        help="Kriteria objektif untuk menentukan klien siap ke tahap berikutnya atau reunifikasi.",
    )

    # -------------------------------------------------------------------------
    # INTEGRASI NPO_ASSESSMENT & NPO_DISBURSEMENT_BASE
    # -------------------------------------------------------------------------
    assessment_id = fields.Many2one(
        comodel_name="npo.assessment",
        string="Asesmen Kemiskinan Terkait",
        domain="[('partner_id', '=', partner_id)]",
        help="Dokumen asesmen kemiskinan dan kelayakan dari npo_assessment.",
    )
    disbursement_request_count = fields.Integer(
        string="Jumlah Penyaluran Manfaat",
        compute="_compute_disbursement_count",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("lks.case.plan")
                vals["name"] = seq or "/"
        return super().create(vals_list)

    def _compute_disbursement_count(self):
        disb_obj = self.env["npo.disbursement.request"]
        for rec in self:
            rec.disbursement_request_count = disb_obj.search_count([("partner_id", "=", rec.partner_id.id)])

    def action_approve(self):
        for rec in self:
            rec.state = "approved"
            if rec.partner_id.service_status in ["intake", "assessment"]:
                rec.partner_id.service_status = "active"

    def action_start_intervention(self):
        for rec in self:
            rec.state = "ongoing"

    def action_evaluate(self):
        for rec in self:
            rec.state = "evaluated"

    def action_close(self):
        for rec in self:
            rec.state = "closed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    def action_set_to_draft(self):
        for rec in self:
            rec.state = "draft"

    def action_create_npo_assessment(self):
        self.ensure_one()
        return {
            "name": _("Buat Asesmen Kelayakan Klien"),
            "type": "ir.actions.act_window",
            "res_model": "npo.assessment",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_surveyor_id": self.social_worker_id.id or self.env.uid,
                "default_survey_type": "initial",
            },
        }

    def action_create_disbursement_request(self):
        self.ensure_one()
        return {
            "name": _("Pengajuan Bantuan / Penyaluran Manfaat"),
            "type": "ir.actions.act_window",
            "res_model": "npo.disbursement.request",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_purpose": f"Bantuan Program Layanan Asuhan PPKS - {self.partner_id.name}",
            },
        }

    def action_view_disbursements(self):
        self.ensure_one()
        action = self.env.ref("npo_disbursement_base.action_npo_disbursement_request").read()[0]
        action["domain"] = [("partner_id", "=", self.partner_id.id)]
        action["context"] = {"default_partner_id": self.partner_id.id}
        return action


class LksCaseTermination(models.Model):
    _name = "lks.case.termination"
    _description = "Terminasi Layanan & Penyatuan Kembali (Reuni Keluarga) PPKS"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "termination_date desc, id desc"

    name = fields.Char(
        string="No. Berita Acara Terminasi",
        required=True,
        copy=False,
        readonly=True,
        default="/",
        tracking=True,
    )
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
    ppks_category_id = fields.Many2one(
        comodel_name="lks.ppks.category",
        string="Kategori PPKS",
        related="partner_id.ppks_category_id",
        store=True,
        readonly=True,
    )
    social_worker_id = fields.Many2one(
        comodel_name="res.users",
        string="Pekerja Sosial Penanggung Jawab",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    termination_date = fields.Date(
        string="Tanggal Efektif Terminasi / Reuni",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    termination_type = fields.Selection(
        selection=[
            ("family_reunion", "Penyatuan Kembali ke Keluarga Kandung / Kerabat (Reunifikasi)"),
            ("legal_adoption", "Pengangkatan Anak Sah (Adopsi Resmi Berdasarkan Penetapan Pengadilan)"),
            ("independence", "Kemandirian (Lulus Sekolah / Masuk Dunia Kerja / Menikah)"),
            ("referral_out", "Rujukan ke Balai Besar Kemensos / Lembaga Spesialis Lain"),
            ("deceased", "Meninggal Dunia"),
            ("other", "Lainnya / Permintaan Keluarga Sendiri"),
        ],
        string="Alasan / Bentuk Terminasi",
        default="family_reunion",
        required=True,
        tracking=True,
    )

    # -------------------------------------------------------------------------
    # DATA KELUARGA / PIHAK PENERIMA REUNIFIKASI
    # -------------------------------------------------------------------------
    reunion_recipient_name = fields.Char(
        string="Nama Lengkap Penerima Klien",
        help="Nama orang tua, wali, keluarga angkat, atau perwakilan instansi rujukan.",
    )
    reunion_relation = fields.Selection(
        selection=[
            ("parent", "Orang Tua Kandung (Ayah/Ibu)"),
            ("grandparent", "Kakek / Nenek"),
            ("uncle_aunt", "Paman / Bibi"),
            ("sibling", "Kakak / Adik"),
            ("adoptive_parent", "Orang Tua Angkat Sah"),
            ("institution", "Pimpinan Balai / LKS Lain"),
            ("self", "Klien Sendiri (Mandiri Dewasa)"),
        ],
        string="Hubungan dengan Klien",
        default="parent",
    )
    reunion_nik = fields.Char(
        string="NIK Penerima",
        size=16,
    )
    reunion_phone = fields.Char(
        string="No. Telepon / WhatsApp Penerima",
    )
    reunion_address = fields.Text(
        string="Alamat Tempat Tinggal Baru Klien",
        help="Alamat lengkap tujuan di mana klien akan bertempat tinggal setelah reunifikasi.",
    )

    # -------------------------------------------------------------------------
    # KESIAPAN REUNIFIKASI & BIMBINGAN LANJUT (AFTERCARE)
    # -------------------------------------------------------------------------
    home_readiness_notes = fields.Text(
        string="Hasil Asesmen Kesiapan Keluarga (Home Visit)",
        help="Catatan kondisi sosial ekonomi keluarga, penerimaan emosional anggota keluarga, dan lingkungan tempat tinggal baru.",
    )
    client_readiness_notes = fields.Text(
        string="Kesiapan Mental & Psikologis Klien",
        help="Kesiapan emosional klien untuk kembali hidup bersama keluarga atau hidup mandiri.",
    )
    aftercare_plan = fields.Text(
        string="Rencana Bimbingan Lanjut (Aftercare)",
        required=True,
        help="Jadwal pemantauan pasca terminasi (Kunjungan rumah bulan ke-1, bulan ke-3, bulan ke-6) untuk memastikan adaptasi berjalan lancar.",
    )
    court_decree_number = fields.Char(
        string="No. Penetapan Pengadilan (Jika Adopsi)",
        help="Nomor Surat Penetapan Pengadilan Negeri/Agama untuk adopsi anak sah.",
    )
    court_decree_file = fields.Binary(
        string="Scan Berkas Penetapan / Surat Adopsi",
        attachment=True,
    )

    # -------------------------------------------------------------------------
    # STATUS & APPROVAL
    # -------------------------------------------------------------------------
    state = fields.Selection(
        selection=[
            ("draft", "Draft Berita Acara"),
            ("verified", "Terverifikasi Peksos"),
            ("approved", "Disetujui Kepala Panti"),
            ("done", "Terminasi Selesai / Klien Diserahkan"),
            ("cancel", "Dibatalkan"),
        ],
        string="Status",
        default="draft",
        tracking=True,
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("lks.case.termination")
                vals["name"] = seq or "/"
        return super().create(vals_list)

    def action_verify(self):
        for rec in self:
            rec.state = "verified"
            if rec.partner_id:
                rec.partner_id.service_status = "pre_reunion"

    def action_approve(self):
        for rec in self:
            rec.state = "approved"

    def action_done(self):
        for rec in self:
            rec.state = "done"
            if rec.partner_id:
                rec.partner_id.write({
                    "service_status": "discharged",
                    "discharge_date": rec.termination_date,
                    "room_id": False,
                    "bed_number": False,
                })

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    def action_set_to_draft(self):
        for rec in self:
            rec.state = "draft"


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Smart button counters for social care
    education_ids = fields.One2many(
        comodel_name="lks.education.record",
        inverse_name="partner_id",
        string="Riwayat Pendidikan",
    )
    education_count = fields.Integer(
        string="Jumlah Catatan Pendidikan",
        compute="_compute_social_care_counts",
    )
    medical_record_ids = fields.One2many(
        comodel_name="lks.medical.record",
        inverse_name="partner_id",
        string="Rekam Medis",
    )
    has_medical_record = fields.Boolean(
        string="Memiliki Rekam Medis",
        compute="_compute_social_care_counts",
    )
    case_plan_ids = fields.One2many(
        comodel_name="lks.case.plan",
        inverse_name="partner_id",
        string="Rencana Intervensi",
    )
    case_plan_count = fields.Integer(
        string="Jumlah Case Plan",
        compute="_compute_social_care_counts",
    )
    termination_ids = fields.One2many(
        comodel_name="lks.case.termination",
        inverse_name="partner_id",
        string="Riwayat Terminasi",
    )
    termination_count = fields.Integer(
        string="Jumlah Berita Acara Terminasi",
        compute="_compute_social_care_counts",
    )

    def _compute_social_care_counts(self):
        for rec in self:
            rec.education_count = len(rec.education_ids)
            rec.has_medical_record = bool(rec.medical_record_ids)
            rec.case_plan_count = len(rec.case_plan_ids)
            rec.termination_count = len(rec.termination_ids)

    def action_view_education_records(self):
        self.ensure_one()
        action = self.env.ref("lks_social_care.action_lks_education_record").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {"default_partner_id": self.id}
        return action

    def action_view_medical_record(self):
        self.ensure_one()
        med = self.medical_record_ids[:1]
        if med:
            return {
                "name": _("Rekam Medis Klien"),
                "type": "ir.actions.act_window",
                "res_model": "lks.medical.record",
                "view_mode": "form",
                "res_id": med.id,
                "target": "current",
            }
        else:
            return {
                "name": _("Buat Rekam Medis Klien"),
                "type": "ir.actions.act_window",
                "res_model": "lks.medical.record",
                "view_mode": "form",
                "target": "current",
                "context": {"default_partner_id": self.id},
            }

    def action_view_case_plans(self):
        self.ensure_one()
        action = self.env.ref("lks_social_care.action_lks_case_plan").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {"default_partner_id": self.id}
        return action

    def action_view_terminations(self):
        self.ensure_one()
        action = self.env.ref("lks_social_care.action_lks_case_termination").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {"default_partner_id": self.id}
        return action
