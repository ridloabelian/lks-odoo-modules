# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # -------------------------------------------------------------------------
    # IDENTIFIKASI PPKS (PEMERLU PELAYANAN KESEJAHTERAAN SOSIAL)
    # -------------------------------------------------------------------------
    is_ppks = fields.Boolean(
        string="Penerima Manfaat PPKS",
        default=False,
        index=True,
        tracking=True,
        help="Centang jika kontak ini adalah binaan / anak asuh / lansia / klien PPKS Kemensos.",
    )
    registration_number = fields.Char(
        string="No. Induk Registrasi PPKS",
        size=32,
        copy=False,
        index=True,
        tracking=True,
        help="Nomor Induk Registrasi Buku Induk Panti (contoh: LKS/2026/0001).",
    )
    ppks_category_id = fields.Many2one(
        comodel_name="lks.ppks.category",
        string="Kategori PPKS Utama",
        index=True,
        tracking=True,
        help="Kategori PPKS Utama dari 26 Kategori Resmi Kemensos RI.",
    )
    ppks_cluster = fields.Selection(
        related="ppks_category_id.cluster",
        string="Kluster PPKS",
        store=True,
        readonly=True,
    )
    ppks_secondary_category_ids = fields.Many2many(
        comodel_name="lks.ppks.category",
        relation="rel_partner_secondary_ppks_category",
        column1="partner_id",
        column2="category_id",
        string="Kategori PPKS Penyerta",
        help="Kategori kerentanan tambahan (misal: Anak Telantar yang juga memiliki Disabilitas Sensorik).",
    )

    # -------------------------------------------------------------------------
    # STATUS RESIDENSIAL & SIKLUS LAYANAN PANTI
    # -------------------------------------------------------------------------
    residential_status = fields.Selection(
        selection=[
            ("in_facility", "Dalam Panti / Asrama (Residensial)"),
            ("day_care", "Penitipan Harian (Day Care)"),
            ("out_facility", "Luar Panti / Bina Keluarga (Non-Residensial)"),
        ],
        string="Status Residensial",
        default="in_facility",
        required=True,
        tracking=True,
        help="Status tempat tinggal klien selama menerima pelayanan kesejahteraan sosial.",
    )
    service_status = fields.Selection(
        selection=[
            ("intake", "Penerimaan / Registrasi Awal"),
            ("assessment", "Proses Asesmen Komprehensif"),
            ("active", "Pelayanan & Pembinaan Aktif"),
            ("pre_reunion", "Persiapan Terminasi / Reuni"),
            ("discharged", "Terminasi / Selesai Pelayanan"),
            ("follow_up", "Bimbingan Lanjut (Aftercare)"),
        ],
        string="Status Layanan",
        default="intake",
        required=True,
        tracking=True,
        index=True,
        help="Tahapan siklus pelayanan sosial (Case Management Standard Kemensos).",
    )
    intake_date = fields.Date(
        string="Tanggal Masuk / Penerimaan",
        default=fields.Date.context_today,
        tracking=True,
        help="Tanggal resmi klien diterima dalam asuhan/pelayanan lembaga.",
    )
    discharge_date = fields.Date(
        string="Tanggal Keluar / Terminasi",
        tracking=True,
        help="Tanggal resmi pengakhiran pelayanan atau penyatuan kembali ke keluarga.",
    )
    duration_of_stay = fields.Integer(
        string="Lama Pelayanan (Bulan)",
        compute="_compute_duration_of_stay",
        store=True,
        help="Lama waktu dalam asuhan/layanan panti (dalam satuan bulan).",
    )

    # -------------------------------------------------------------------------
    # SUMBER RUJUKAN
    # -------------------------------------------------------------------------
    referral_source = fields.Selection(
        selection=[
            ("dinsos", "Dinas Sosial (Provinsi / Kab / Kota)"),
            ("police", "Kepolisian / Aparat Penegak Hukum"),
            ("hospital", "Rumah Sakit / Puskesmas / Faskes"),
            ("community", "Masyarakat / RT / RW / Tokoh Masyarakat"),
            ("family", "Keluarga / Kerabat"),
            ("self", "Datang Sendiri / Inisiatif Mandiri"),
            ("other_lks", "Rujukan LKS / Lembaga Sosial Lain"),
        ],
        string="Sumber Rujukan",
        default="family",
        tracking=True,
    )
    referral_notes = fields.Text(
        string="Catatan & Dokumen Rujukan",
        help="Keterangan surat pengantar dari Dinas Sosial atau pihak perujuk.",
    )

    # -------------------------------------------------------------------------
    # FASILITAS RESIDENSIAL (ASRAMA & KAMAR)
    # -------------------------------------------------------------------------
    dormitory_id = fields.Many2one(
        comodel_name="lks.facility.dormitory",
        string="Gedung / Asrama",
        domain="[('company_id', '=', company_id)]",
        tracking=True,
    )
    room_id = fields.Many2one(
        comodel_name="lks.facility.room",
        string="Kamar / Ruangan",
        domain="[('dormitory_id', '=?', dormitory_id)]",
        tracking=True,
    )
    bed_number = fields.Char(
        string="Nomor Bed / Kasur",
        help="Identifikasi nomor tempat tidur klien.",
    )

    # -------------------------------------------------------------------------
    # DATA WALI / KELUARGA PENANGGUNG JAWAB
    # -------------------------------------------------------------------------
    guardian_id = fields.Many2one(
        comodel_name="res.partner",
        string="Wali / Kontak Keluarga",
        domain="[('id', '!=', id)]",
        tracking=True,
    )
    guardian_relation = fields.Selection(
        selection=[
            ("parent", "Orang Tua Kandung (Ayah/Ibu)"),
            ("step_parent", "Orang Tua Tiri / Sambung"),
            ("grandparent", "Kakek / Nenek"),
            ("uncle_aunt", "Paman / Bibi"),
            ("sibling", "Kakak / Adik"),
            ("foster_parent", "Orang Tua Asuh"),
            ("legal_guardian", "Wali Hukum Sah Pengadilan"),
            ("none", "Sebatang Kara / Tidak Diketahui"),
        ],
        string="Hubungan dengan Klien",
        default="parent",
    )
    guardian_phone = fields.Char(
        string="No. Telepon Wali",
        related="guardian_id.phone",
        readonly=True,
    )
    guardian_address = fields.Text(
        string="Alamat Domisili Wali",
        related="guardian_id.full_administrative_address",
        readonly=True,
    )

    # -------------------------------------------------------------------------
    # PETUGAS PENDAMPING (PEKERJA SOSIAL / SAKTI PEKSOS)
    # -------------------------------------------------------------------------
    social_worker_id = fields.Many2one(
        comodel_name="res.users",
        string="Pekerja Sosial Pendamping (Peksos)",
        tracking=True,
        help="Pekerja Sosial atau Petugas Pendamping Utama yang bertanggung jawab (Case Manager).",
    )
    peksos_registration_no = fields.Char(
        string="No. Sertifikat / STR Peksos",
        help="Nomor Surat Tanda Registrasi (STR) Pekerja Sosial Kemensos RI.",
    )
    peksos_phone = fields.Char(
        string="No. Kontak Peksos",
        related="social_worker_id.phone",
        readonly=True,
    )

    # -------------------------------------------------------------------------
    # BUKU INDUK PENERIMAAN LOG
    # -------------------------------------------------------------------------
    admission_register_ids = fields.One2many(
        comodel_name="lks.admission.register",
        inverse_name="partner_id",
        string="Riwayat Buku Induk Registrasi",
    )
    admission_count = fields.Integer(
        string="Jumlah Registrasi",
        compute="_compute_admission_count",
    )

    if hasattr(models, "Constraint"):
        _registration_number_uniq = models.Constraint(
            "unique(registration_number, company_id)",
            "Nomor Induk Registrasi PPKS sudah digunakan dalam lembaga ini! Harus unik.",
        )
    else:
        _sql_constraints = [
            (
                "registration_number_uniq",
                "unique(registration_number, company_id)",
                "Nomor Induk Registrasi PPKS sudah digunakan dalam lembaga ini! Harus unik.",
            ),
        ]

    @api.depends("admission_register_ids")
    def _compute_admission_count(self):
        for rec in self:
            rec.admission_count = len(rec.admission_register_ids)

    @api.depends("intake_date", "discharge_date")
    def _compute_duration_of_stay(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.intake_date:
                end_date = rec.discharge_date or today
                if end_date >= rec.intake_date:
                    delta_years = end_date.year - rec.intake_date.year
                    delta_months = end_date.month - rec.intake_date.month
                    total_months = (delta_years * 12) + delta_months
                    rec.duration_of_stay = max(1, total_months)
                else:
                    rec.duration_of_stay = 0
            else:
                rec.duration_of_stay = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("is_ppks") and not vals.get("registration_number"):
                # Buat nomor registrasi otomatis jika belum diisi
                seq = self.env["ir.sequence"].next_by_code("lks.ppks.registration")
                vals["registration_number"] = seq or "/"
                # Set otomatis is_npo_beneficiary
                vals["is_npo_beneficiary"] = True
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("is_ppks"):
            vals["is_npo_beneficiary"] = True
            for rec in self:
                if not rec.registration_number and not vals.get("registration_number"):
                    vals["registration_number"] = self.env["ir.sequence"].next_by_code("lks.ppks.registration") or "/"
        return super().write(vals)

    @api.constrains("is_ppks", "ppks_category_id")
    def _check_ppks_category(self):
        for rec in self:
            if rec.is_ppks and not rec.ppks_category_id:
                raise ValidationError(_("Penerima Manfaat PPKS wajib memiliki 'Kategori PPKS Utama'!"))

    @api.onchange("dormitory_id")
    def _onchange_dormitory_id(self):
        if self.dormitory_id and self.room_id and self.room_id.dormitory_id != self.dormitory_id:
            self.room_id = False

    def action_view_admission_registers(self):
        self.ensure_one()
        action = self.env.ref("lks_core.action_lks_admission_register").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {"default_partner_id": self.id}
        return action
