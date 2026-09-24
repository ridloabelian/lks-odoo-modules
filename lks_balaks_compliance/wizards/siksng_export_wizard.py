# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64
import csv
import io
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LksSiksngExportWizard(models.TransientModel):
    _name = "lks.siksng.export.wizard"
    _description = "Wizard Ekspor Data Binaan Format SIKS-NG Kemensos & Dinsos"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        default=lambda self: self.env.company,
        required=True,
    )
    ppks_category_id = fields.Many2one(
        comodel_name="lks.ppks.category",
        string="Filter Kategori PPKS",
        help="Biarkan kosong untuk mengekspor semua 26 kategori.",
    )
    residential_status = fields.Selection(
        selection=[
            ("all", "Semua Status Residensial"),
            ("in_facility", "Hanya Dalam Panti (Residensial)"),
            ("out_facility", "Hanya Luar Panti (Bina Keluarga)"),
            ("day_care", "Hanya Day Care"),
        ],
        string="Status Residensial",
        default="all",
        required=True,
    )
    service_status = fields.Selection(
        selection=[
            ("active", "Hanya Klien Aktif (Intake/Asesmen/Binaan Aktif)"),
            ("discharged", "Hanya Klien yang Sudah Terminasi / Reuni"),
            ("all", "Semua Klien (Aktif & Terminasi)"),
        ],
        string="Status Pelayanan",
        default="active",
        required=True,
    )
    file_format = fields.Selection(
        selection=[
            ("csv", "CSV (Format Standar SIKS-NG Kemensos)"),
        ],
        string="Format Berkas",
        default="csv",
        required=True,
    )
    export_file = fields.Binary(
        string="Unduh File Ekspor",
        readonly=True,
    )
    export_filename = fields.Char(
        string="Nama File",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Pilih Filter"),
            ("done", "Siap Diunduh"),
        ],
        string="Status",
        default="draft",
    )

    def action_generate_export(self):
        self.ensure_one()
        partner_obj = self.env["res.partner"]

        domain = [
            ("is_ppks", "=", True),
            ("company_id", "=", self.company_id.id),
        ]
        if self.ppks_category_id:
            domain.append(("ppks_category_id", "=", self.ppks_category_id.id))

        if self.residential_status != "all":
            domain.append(("residential_status", "=", self.residential_status))

        if self.service_status == "active":
            domain.append(("service_status", "in", ["intake", "assessment", "active"]))
        elif self.service_status == "discharged":
            domain.append(("service_status", "in", ["pre_reunion", "discharged", "follow_up"]))

        clients = partner_obj.search(domain, order="intake_date desc, id desc")
        if not clients:
            raise UserError(_("Tidak ditemukan data klien PPKS yang sesuai dengan filter yang dipilih!"))

        # Siapkan CSV dengan UTF-8 BOM agar terbaca sempurna di Microsoft Excel
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        # Header Kolom Standar SIKS-NG Kemensos & Dinsos
        headers = [
            "NO",
            "NO_INDUK_PPKS",
            "NO_KARTU_KELUARGA",
            "NIK_KTP",
            "NAMA_LENGKAP",
            "TEMPAT_LAHIR",
            "TANGGAL_LAHIR",
            "JENIS_KELAMIN",
            "AGAMA",
            "STATUS_PERKAWINAN",
            "PENDIDIKAN_TERAKHIR",
            "KATEGORI_PPKS",
            "KODE_PPKS",
            "KLUSTER_PPKS",
            "STATUS_RESIDENSIAL",
            "ASRAMA_GEDUNG",
            "KAMAR_RUANGAN",
            "NO_BED",
            "ALAMAT_ASAL",
            "RT",
            "RW",
            "DESA_KELURAHAN",
            "KECAMATAN",
            "KAB_KOTA",
            "PROVINSI",
            "KODE_POS",
            "NAMA_WALI_KELUARGA",
            "HUBUNGAN_WALI",
            "TELEPON_WALI",
            "PEKERJA_SOSIAL_PENDAMPING",
            "NO_STR_PEKSOS",
            "TANGGAL_MASUK_PANTI",
            "TANGGAL_TERMINASI",
            "STATUS_LAYANAN",
        ]
        writer.writerow(headers)

        gender_map = {"male": "Laki-laki", "female": "Perempuan"}
        residence_map = {
            "in_facility": "Dalam Panti (Residensial)",
            "day_care": "Day Care",
            "out_facility": "Luar Panti (Bina Keluarga)",
        }
        service_map = {
            "intake": "Penerimaan Awal",
            "assessment": "Proses Asesmen",
            "active": "Pelayanan Aktif",
            "pre_reunion": "Persiapan Reuni",
            "discharged": "Terminasi Selesai",
            "follow_up": "Bimbingan Lanjut",
        }

        for idx, c in enumerate(clients, start=1):
            writer.writerow([
                idx,
                c.registration_number or "",
                c.kk_number or "",
                c.nik or "",
                c.name or "",
                c.birth_place or "",
                c.birth_date.strftime("%d/%m/%Y") if c.birth_date else "",
                gender_map.get(c.gender, ""),
                c.religion or "",
                c.marital_status or "",
                c.last_education or "",
                c.ppks_category_id.name if c.ppks_category_id else "",
                c.ppks_category_id.code if c.ppks_category_id else "",
                c.ppks_cluster or "",
                residence_map.get(c.residential_status, ""),
                c.dormitory_id.name if c.dormitory_id else "",
                c.room_id.name if c.room_id else "",
                c.bed_number or "",
                c.street or "",
                c.rt or "",
                c.rw or "",
                c.village_id.name if c.village_id else "",
                c.district_id.name if c.district_id else "",
                c.regency_id.name if c.regency_id else "",
                c.province_id.name if c.province_id else "",
                c.postal_code or "",
                c.guardian_id.name if c.guardian_id else "",
                c.guardian_relation or "",
                c.guardian_phone or "",
                c.social_worker_id.name if c.social_worker_id else "",
                c.peksos_registration_no or "",
                c.intake_date.strftime("%d/%m/%Y") if c.intake_date else "",
                c.discharge_date.strftime("%d/%m/%Y") if c.discharge_date else "",
                service_map.get(c.service_status, ""),
            ])

        csv_data = output.getvalue()
        output.close()

        # Tambahkan BOM UTF-8 (\xef\xbb\xbf) agar Excel membaca karakter Indonesia dengan rapi
        bom_csv = "\ufeff" + csv_data
        encoded_file = base64.b64encode(bom_csv.encode("utf-8"))

        clean_comp = "".join(filter(str.isalnum, self.company_id.name or "LKS"))
        filename = f"Data_Binaan_SIKSNG_{clean_comp}_{fields.Date.today().strftime('%Y%m%d')}.csv"

        self.write({
            "export_file": encoded_file,
            "export_filename": filename,
            "state": "done",
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": "lks.siksng.export.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }
