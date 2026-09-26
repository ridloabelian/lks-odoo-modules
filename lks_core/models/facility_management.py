# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LksFacilityDormitory(models.Model):
    _name = "lks.facility.dormitory"
    _description = "Gedung / Asrama / Wisma Fasilitas Panti"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name asc"

    name = fields.Char(
        string="Nama Asrama / Wisma",
        required=True,
        tracking=True,
        help="Contoh: Asrama Putra Al-Ikhlas, Wisma Lansia Melati, Asrama Balita Harapan",
    )
    code = fields.Char(
        string="Kode Asrama",
        size=10,
        required=True,
        index=True,
    )
    facility_type = fields.Selection(
        selection=[
            ("orphanage", "Panti Asuhan Anak (LKS Anak)"),
            ("elderly", "Panti Wreda / Griya Lansia (LKS Lansia)"),
            ("disability", "Panti Rehabilitasi Disabilitas"),
            ("shelter", "Rumah Singgah / Shelter Sosial"),
            ("daycare", "Fasilitas Harian (Day Care)"),
            ("other", "Fasilitas Sosial Lainnya"),
        ],
        string="Jenis Fasilitas",
        default="orphanage",
        required=True,
        tracking=True,
    )
    gender_target = fields.Selection(
        selection=[
            ("male", "Khusus Putra / Laki-laki"),
            ("female", "Khusus Putri / Perempuan"),
            ("mixed", "Campur (Keluarga / Balita)"),
        ],
        string="Target Penghuni",
        default="male",
        required=True,
        tracking=True,
    )
    room_ids = fields.One2many(
        comodel_name="lks.facility.room",
        inverse_name="dormitory_id",
        string="Daftar Kamar",
    )
    room_count = fields.Integer(
        string="Jumlah Kamar",
        compute="_compute_counts",
        store=True,
    )
    total_capacity = fields.Integer(
        string="Kapasitas Total (Tempat Tidur)",
        compute="_compute_counts",
        store=True,
        tracking=True,
    )
    total_occupants = fields.Integer(
        string="Penghuni Saat Ini",
        compute="_compute_counts",
        store=True,
    )
    available_beds = fields.Integer(
        string="Tempat Tidur Kosong",
        compute="_compute_counts",
        store=True,
    )
    occupancy_rate = fields.Float(
        string="Tingkat Hunian (%)",
        compute="_compute_counts",
        store=True,
    )
    manager_id = fields.Many2one(
        comodel_name="res.users",
        string="Kepala Asrama / Penanggung Jawab",
        tracking=True,
    )
    caregiver_ids = fields.Many2many(
        comodel_name="res.users",
        string="Petugas Pengasuh / Caregiver Bertugas",
    )
    address = fields.Text(
        string="Alamat / Lokasi Gedung",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        default=lambda self: self.env.company,
        required=True,
    )
    active = fields.Boolean(
        string="Aktif",
        default=True,
    )

    if hasattr(models, "Constraint"):
        _code_company_uniq = models.Constraint("unique(code, company_id)", "Kode Asrama harus unik untuk setiap lembaga!")
    else:
        _sql_constraints = [
            ("code_company_uniq", "unique(code, company_id)", "Kode Asrama harus unik untuk setiap lembaga!"),
        ]

    @api.depends("room_ids.capacity", "room_ids.occupant_count")
    def _compute_counts(self):
        for rec in self:
            rec.room_count = len(rec.room_ids)
            rec.total_capacity = sum(rec.room_ids.mapped("capacity"))
            rec.total_occupants = sum(rec.room_ids.mapped("occupant_count"))
            rec.available_beds = rec.total_capacity - rec.total_occupants
            if rec.total_capacity > 0:
                rec.occupancy_rate = round((rec.total_occupants / rec.total_capacity) * 100.0, 1)
            else:
                rec.occupancy_rate = 0.0


class LksFacilityRoom(models.Model):
    _name = "lks.facility.room"
    _description = "Kamar / Ruangan Fasilitas Panti"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "dormitory_id asc, name asc"

    name = fields.Char(
        string="Nama / Nomor Kamar",
        required=True,
        tracking=True,
        help="Contoh: Kamar 01, Kamar Cempaka, Ruang Melati 2",
    )
    dormitory_id = fields.Many2one(
        comodel_name="lks.facility.dormitory",
        string="Gedung / Asrama",
        required=True,
        ondelete="cascade",
        index=True,
        tracking=True,
    )
    floor = fields.Selection(
        selection=[
            ("1", "Lantai 1 / Dasar"),
            ("2", "Lantai 2"),
            ("3", "Lantai 3"),
            ("4", "Lantai 4"),
        ],
        string="Lantai",
        default="1",
    )
    capacity = fields.Integer(
        string="Kapasitas Bed (Orang)",
        required=True,
        default=4,
        tracking=True,
        help="Jumlah maksimal tempat tidur dalam ruangan ini.",
    )
    occupant_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="room_id",
        string="Daftar Penghuni Saat Ini",
        domain=[("is_ppks", "=", True), ("residential_status", "=", "in_facility"), ("service_status", "in", ["intake", "assessment", "active"])],
    )
    occupant_count = fields.Integer(
        string="Jumlah Penghuni",
        compute="_compute_occupants",
        store=True,
    )
    available_beds = fields.Integer(
        string="Sisa Bed Kosong",
        compute="_compute_occupants",
        store=True,
    )
    status = fields.Selection(
        selection=[
            ("available", "Tersedia"),
            ("full", "Penuh"),
            ("maintenance", "Perbaikan / Renovasi"),
            ("quarantine", "Ruang Isolasi / Khusus"),
        ],
        string="Status Kamar",
        compute="_compute_status",
        store=True,
        tracking=True,
    )
    amenities = fields.Char(
        string="Fasilitas Kamar",
        help="Contoh: Kasur Busa, Lemari Pakaian, Kipas Angin, Kamar Mandi Dalam",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        related="dormitory_id.company_id",
        store=True,
        readonly=True,
    )

    if hasattr(models, "Constraint"):
        _name_dormitory_uniq = models.Constraint("unique(name, dormitory_id)", "Nama/Nomor Kamar dalam asrama yang sama harus unik!")
    else:
        _sql_constraints = [
            ("name_dormitory_uniq", "unique(name, dormitory_id)", "Nama/Nomor Kamar dalam asrama yang sama harus unik!"),
        ]

    @api.depends("occupant_ids")
    def _compute_occupants(self):
        for rec in self:
            rec.occupant_count = len(rec.occupant_ids)
            rec.available_beds = max(0, rec.capacity - rec.occupant_count)

    @api.depends("capacity", "occupant_count")
    def _compute_status(self):
        for rec in self:
            if rec.occupant_count >= rec.capacity:
                rec.status = "full"
            else:
                rec.status = "available"

    @api.constrains("occupant_count", "capacity")
    def _check_capacity(self):
        for rec in self:
            if rec.occupant_count > rec.capacity:
                raise ValidationError(
                    _(
                        "Kamar '%(room)s' melebihi kapasitas maksimal! "
                        "Kapasitas: %(cap)d orang, namun diisi %(occ)d orang."
                    )
                    % {"room": rec.name, "cap": rec.capacity, "occ": rec.occupant_count}
                )

    @api.depends("name", "dormitory_id.name")
    def _compute_display_name(self):
        for rec in self:
            dorm_name = rec.dormitory_id.name if rec.dormitory_id else ""
            rec.display_name = f"{dorm_name} - {rec.name}" if dorm_name else rec.name
