# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    isak35_restriction = fields.Selection(
        selection=[
            ("unrestricted", "Tanpa Pembatasan (Unrestricted)"),
            ("restricted", "Dengan Pembatasan (Restricted)"),
        ],
        string="Sifat Pembatasan ISAK 35",
        default="unrestricted",
        tracking=True,
        help="Menentukan apakah transaksi jurnal ini terikat pembatasan oleh donor/pemberi sumber daya.",
    )
    donor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lembaga Donor / Sumber Dana",
        help="Pihak penyedia hibah / donor jika transaksi berkaitan dengan hibah terikat.",
    )
    program_cluster = fields.Selection(
        selection=[
            ("anak", "Kluster Asuhan Anak"),
            ("lansia", "Kluster Panti Lansia"),
            ("disabilitas", "Kluster Disabilitas"),
            ("tunasosial", "Kluster Tuna Sosial / Napza"),
            ("korban", "Kluster Korban Bencana & Kekerasan"),
            ("umum", "Umum, Operasional & Manajemen"),
        ],
        string="Kluster Program Sosial",
        default="umum",
        help="Alokasi program sosial sesuai kluster PPKS Kemensos RI.",
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    isak35_restriction = fields.Selection(
        related="move_id.isak35_restriction",
        string="Pembatasan ISAK 35",
        store=True,
        readonly=True,
    )
    donor_id = fields.Many2one(
        related="move_id.donor_id",
        string="Lembaga Donor",
        store=True,
        readonly=True,
    )
    program_cluster = fields.Selection(
        related="move_id.program_cluster",
        string="Kluster Program",
        store=True,
        readonly=True,
    )
