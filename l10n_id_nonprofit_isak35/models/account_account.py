# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    isak35_group = fields.Selection(
        selection=[
            ("asset_current", "Aset Lancar (Kas, Bank, Piutang, Persediaan)"),
            ("asset_non_current", "Aset Tidak Lancar (Aset Tetap & Akumulasi Penyusutan)"),
            ("liability_current", "Liabilitas Jangka Pendek (Utang Usaha, Beban Masih Harus Dibayar)"),
            ("liability_non_current", "Liabilitas Jangka Panjang"),
            ("equity_unrestricted", "Aset Neto Tanpa Pembatasan (Unrestricted Net Assets)"),
            ("equity_restricted", "Aset Neto Dengan Pembatasan (Restricted Net Assets)"),
            ("revenue_unrestricted", "Pendapatan Tanpa Pembatasan (Sumbangan Bebas, Jasa Layanan)"),
            ("revenue_restricted", "Pendapatan Dengan Pembatasan (Hibah Terikat Pemerintah/Donor)"),
            ("net_assets_released", "Aset Neto Terbebaskan dari Pembatasan (Penyelesaian Program)"),
            ("expense_program", "Beban Program Pelayanan Sosial (Permakanan, Pendidikan, Kesehatan)"),
            ("expense_support", "Beban Manajemen, Administrasi Umum & Fundraising"),
        ],
        string="Klasifikasi ISAK 35",
        help="Kelompok akun untuk penyusunan 4 Laporan Keuangan Nonlaba berbasis ISAK 35.",
        index=True,
    )

    isak35_cash_flow_category = fields.Selection(
        selection=[
            ("operating", "Aktivitas Operasi"),
            ("investing", "Aktivitas Investasi (Perolehan/Pelepasan Aset Tetap)"),
            ("financing", "Aktivitas Pendanaan (Penerimaan Hibah Terikat Jangka Panjang)"),
            ("cash_equivalent", "Kas & Setara Kas"),
            ("none", "Non-Kas / Tidak Masuk Arus Kas"),
        ],
        string="Kategori Arus Kas ISAK 35",
        default="operating",
        help="Klasifikasi pos untuk penyusunan Laporan Arus Kas Nonlaba.",
    )
