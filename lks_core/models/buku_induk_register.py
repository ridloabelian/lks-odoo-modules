# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LksAdmissionRegister(models.Model):
    _name = "lks.admission.register"
    _description = "Buku Induk Registrasi Penerimaan PPKS"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_received desc, id desc"

    name = fields.Char(
        string="No. Berita Acara Penerimaan",
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
        tracking=True,
        domain="[('is_ppks', '=', True)]",
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
    residential_status = fields.Selection(
        related="partner_id.residential_status",
        string="Status Residensial",
        store=True,
        readonly=True,
    )
    date_received = fields.Date(
        string="Tanggal Penerimaan",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    # Pihak Penyerah
    surrenderer_type = fields.Selection(
        selection=[
            ("dinsos", "Dinas Sosial / Satpol PP"),
            ("police", "Kepolisian / Pengadilan"),
            ("hospital", "Rumah Sakit / Puskesmas"),
            ("community", "Aparat Desa / RT / RW / Tokoh Masyarakat"),
            ("family", "Orang Tua / Wali / Kerabat"),
            ("other", "Lainnya / Inisiatif Mandiri"),
        ],
        string="Pihak yang Menyerahkan",
        default="family",
        required=True,
        tracking=True,
    )
    surrenderer_name = fields.Char(
        string="Nama Lengkap Penyerah",
        required=True,
        help="Nama orang tua, wali, petugas Dinsos, atau saksi penyerahan.",
    )
    surrenderer_institution = fields.Char(
        string="Instansi / Hubungan Keluarga",
        help="Contoh: Dinsos Kota Bandung, Ibu Kandung, Polsek Coblong",
    )
    surrenderer_id_card = fields.Char(
        string="NIK / No. Identitas Penyerah",
    )
    surrenderer_phone = fields.Char(
        string="No. Telepon Penyerah",
    )
    surrenderer_address = fields.Text(
        string="Alamat Penyerah",
    )
    # Petugas Penerima
    receiver_id = fields.Many2one(
        comodel_name="res.users",
        string="Petugas Penerima (Staf Panti)",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    social_worker_id = fields.Many2one(
        comodel_name="res.users",
        string="Pekerja Sosial yang Ditugaskan",
        tracking=True,
    )
    # Asesmen Awal Saat Penerimaan
    intake_reason = fields.Text(
        string="Alasan Penyerahan / Latar Belakang",
        required=True,
        help="Penjelasan latar belakang mengapa klien dimasukkan ke lembaga/panti.",
    )
    initial_physical_condition = fields.Text(
        string="Kondisi Fisik Awal",
        help="Catatan luka, penyakit, gizi, pakaian, atau kondisi kesehatan saat tiba.",
    )
    initial_mental_condition = fields.Text(
        string="Kondisi Mental / Perilaku Awal",
        help="Kondisi emosi, trauma, kecemasan, komunikasi awal klien.",
    )
    belongings_brought = fields.Text(
        string="Barang / Dokumen yang Dibawa",
        help="Daftar pakaian, akta kelahiran, kartu keluarga, kartu BPJS, atau barang berharga yang dibawa saat masuk.",
    )
    witness_name = fields.Char(
        string="Nama Saksi Penyerahan",
    )
    # Status
    state = fields.Selection(
        selection=[
            ("draft", "Draft Berita Acara"),
            ("verified", "Terverifikasi Petugas"),
            ("approved", "Disetujui Pimpinan Panti"),
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
                seq = self.env["ir.sequence"].next_by_code("lks.admission.register")
                vals["name"] = seq or "/"
        return super().create(vals_list)

    def action_verify(self):
        for rec in self:
            rec.state = "verified"

    def action_approve(self):
        for rec in self:
            rec.state = "approved"
            # Update client service status and intake date if needed
            if rec.partner_id:
                rec.partner_id.write({
                    "service_status": "assessment",
                    "intake_date": rec.date_received,
                    "referral_source": rec.surrenderer_type,
                    "social_worker_id": rec.social_worker_id.id or rec.partner_id.social_worker_id.id,
                })

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    def action_set_to_draft(self):
        for rec in self:
            rec.state = "draft"
