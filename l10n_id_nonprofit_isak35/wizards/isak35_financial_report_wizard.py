# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Isak35FinancialReportWizard(models.TransientModel):
    _name = "isak35.financial.report.wizard"
    _description = "Wizard Laporan Keuangan Organisasi Nonlaba (ISAK 35)"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Lembaga / Yayasan",
        default=lambda self: self.env.company,
        required=True,
    )
    date_from = fields.Date(
        string="Tanggal Mulai",
        default=lambda self: date(date.today().year, 1, 1),
        required=True,
    )
    date_to = fields.Date(
        string="Tanggal Selesai",
        default=fields.Date.context_today,
        required=True,
    )
    report_type = fields.Selection(
        selection=[
            ("all", "Paket Lengkap 4 Laporan Keuangan ISAK 35"),
            ("position", "1. Laporan Posisi Keuangan"),
            ("activities", "2. Laporan Penghasilan Komprehensif (Laporan Aktivitas)"),
            ("net_assets", "3. Laporan Perubahan Aset Neto"),
            ("cash_flow", "4. Laporan Arus Kas"),
        ],
        string="Jenis Laporan",
        default="all",
        required=True,
    )
    target_move = fields.Selection(
        selection=[
            ("posted", "Semua Entri yang Diposting (Posted Only)"),
            ("all", "Semua Entri (Termasuk Draft)"),
        ],
        string="Target Jurnal",
        default="posted",
        required=True,
    )

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref("l10n_id_nonprofit_isak35.action_report_isak35_financial").report_action(self)

    def get_financial_report_data(self):
        """Menghitung agregasi saldo akuntansi sesuai format resmi ISAK 35 IAI."""
        self.ensure_one()
        aml_obj = self.env["account.move.line"]

        domain_base = [
            ("company_id", "=", self.company_id.id),
        ]
        if self.target_move == "posted":
            domain_base.append(("move_id.state", "=", "posted"))

        # Domain hingga tanggal akhir (untuk Posisi Keuangan / Neraca)
        domain_balance = domain_base + [("date", "<=", self.date_to)]

        opening_move_id = self.company_id.account_opening_move_id.id if self.company_id.account_opening_move_id else 0

        # Domain dalam periode berjalan (untuk Laporan Aktivitas / Arus Kas, tidak memasukkan saldo awal)
        domain_period = domain_base + [
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]
        if opening_move_id:
            domain_period.append(("move_id", "!=", opening_move_id))

        def get_account_group_balance(group_code, domain):
            # Positif untuk debet, negatif untuk kredit
            lines = aml_obj.search(domain + [("account_id.isak35_group", "=", group_code)])
            return sum(lines.mapped("balance"))

        # ---------------------------------------------------------------------
        # 1. LAPORAN PENGHASILAN KOMPREHENSIF / AKTIVITAS
        # ---------------------------------------------------------------------
        rev_unrestricted = abs(sum(
            aml_obj.search(domain_period + [
                ("account_id.account_type", "in", ["income", "income_other"]),
                ("account_id.isak35_group", "=", "revenue_unrestricted"),
            ]).mapped("balance")
        ))
        rev_restricted = abs(sum(
            aml_obj.search(domain_period + [
                ("account_id.account_type", "in", ["income", "income_other"]),
                ("account_id.isak35_group", "=", "revenue_restricted"),
            ]).mapped("balance")
        ))
        exp_program = abs(sum(
            aml_obj.search(domain_period + [
                ("account_id.account_type", "in", ["expense", "expense_direct_cost"]),
                ("account_id.isak35_group", "=", "expense_program"),
            ]).mapped("balance")
        ))
        exp_support = abs(sum(
            aml_obj.search(domain_period + [
                ("account_id.account_type", "in", ["expense", "expense_depreciation"]),
                ("account_id.isak35_group", "in", ["expense_support", False]),
            ]).mapped("balance")
        ))
        total_expenses = exp_program + exp_support

        released_assets = abs(get_account_group_balance("net_assets_released", domain_period))
        if released_assets == 0.0 and rev_restricted > 0.0 and exp_program > 0.0:
            released_assets = min(rev_restricted, exp_program)

        change_unrestricted = (rev_unrestricted + released_assets) - total_expenses
        change_restricted = rev_restricted - released_assets
        change_total = change_unrestricted + change_restricted

        # ---------------------------------------------------------------------
        # 2. LAPORAN PERUBAHAN ASET NETO
        # ---------------------------------------------------------------------
        beginning_unrestricted = abs(sum(
            aml_obj.search(domain_base + [
                ("account_id.isak35_group", "=", "equity_unrestricted"),
                "|", ("date", "<", self.date_from), ("move_id", "=", opening_move_id),
            ]).mapped("balance")
        ))
        beginning_restricted = abs(sum(
            aml_obj.search(domain_base + [
                ("account_id.isak35_group", "=", "equity_restricted"),
                "|", ("date", "<", self.date_from), ("move_id", "=", opening_move_id),
            ]).mapped("balance")
        ))
        if beginning_unrestricted == 0.0 and beginning_restricted == 0.0 and opening_move_id:
            beginning_unrestricted = abs(sum(
                aml_obj.search([("move_id", "=", opening_move_id), ("account_id.account_type", "=", "equity")]).mapped("balance")
            ))
        beginning_total = beginning_unrestricted + beginning_restricted

        ending_unrestricted = beginning_unrestricted + change_unrestricted
        ending_restricted = beginning_restricted + change_restricted
        ending_total = ending_unrestricted + ending_restricted

        # ---------------------------------------------------------------------
        # 3. LAPORAN ARUS KAS
        # ---------------------------------------------------------------------
        cash_operating = (rev_unrestricted + rev_restricted) - total_expenses
        cash_investing = -abs(sum(
            aml_obj.search(domain_period + [
                ("account_id.isak35_cash_flow_category", "=", "investing"),
            ]).mapped("balance")
        ))
        cash_financing = abs(sum(
            aml_obj.search(domain_period + [
                ("account_id.isak35_cash_flow_category", "=", "financing"),
            ]).mapped("balance")
        ))
        net_cash_flow = cash_operating + cash_investing + cash_financing
        beginning_cash = sum(
            aml_obj.search(domain_base + [
                ("account_id.account_type", "in", ["asset_cash"]),
                "|", ("date", "<", self.date_from), ("move_id", "=", opening_move_id),
            ]).mapped("balance")
        )
        ending_cash = beginning_cash + net_cash_flow

        # ---------------------------------------------------------------------
        # 4. LAPORAN POSISI KEUANGAN
        # ---------------------------------------------------------------------
        total_cash = sum(
            aml_obj.search(domain_balance + [
                ("account_id.account_type", "in", ["asset_cash"]),
            ]).mapped("balance")
        )
        raw_cash_restricted = min(total_cash, max(0.0, ending_restricted))
        raw_cash_unrestricted = max(0.0, total_cash - raw_cash_restricted)

        raw_receivables = sum(
            aml_obj.search(domain_balance + [
                ("account_id.account_type", "in", ["asset_receivable"]),
                ("account_id.isak35_group", "=", "asset_current"),
            ]).mapped("balance")
        )
        other_current_assets = sum(
            aml_obj.search(domain_balance + [
                ("account_id.account_type", "in", ["asset_current", "asset_prepayments"]),
                ("account_id.isak35_group", "=", "asset_current"),
            ]).mapped("balance")
        )
        if other_current_assets < 0:
            other_current_assets = 0.0

        current_assets = max(0.0, raw_cash_unrestricted + raw_cash_restricted + raw_receivables + other_current_assets)
        fixed_assets = max(0.0, get_account_group_balance("asset_non_current", domain_balance))
        total_assets = current_assets + fixed_assets

        # LIABILITAS
        current_liabilities = abs(sum(
            aml_obj.search(domain_balance + [
                ("account_id.account_type", "in", ["liability_payable", "liability_current"]),
            ]).mapped("balance")
        ))
        non_current_liabilities = abs(sum(
            aml_obj.search(domain_balance + [
                ("account_id.account_type", "in", ["liability_non_current"]),
            ]).mapped("balance")
        ))
        total_liabilities = current_liabilities + non_current_liabilities

        # ASET NETO (EQUITY)
        net_assets_unrestricted = ending_unrestricted
        net_assets_restricted = ending_restricted
        total_net_assets = ending_total
        total_liabilities_and_net_assets = total_liabilities + total_net_assets

        return {
            "company_name": self.company_id.name,
            "currency_symbol": self.company_id.currency_id.symbol or "Rp",
            "date_from": self.date_from,
            "date_to": self.date_to,
            "report_type": self.report_type,
            # Posisi Keuangan
            "cash_unrestricted": raw_cash_unrestricted,
            "cash_restricted": raw_cash_restricted,
            "receivables": raw_receivables,
            "other_current_assets": other_current_assets,
            "current_assets": current_assets,
            "fixed_assets": fixed_assets,
            "total_assets": total_assets,
            "current_liabilities": current_liabilities,
            "non_current_liabilities": non_current_liabilities,
            "total_liabilities": total_liabilities,
            "net_assets_unrestricted": net_assets_unrestricted,
            "net_assets_restricted": net_assets_restricted,
            "total_net_assets": total_net_assets,
            "total_liabilities_and_net_assets": total_liabilities_and_net_assets,
            # Aktivitas
            "rev_unrestricted": rev_unrestricted,
            "rev_restricted": rev_restricted,
            "released_assets": released_assets,
            "total_rev_unrestricted": rev_unrestricted + released_assets,
            "exp_program": exp_program,
            "exp_support": exp_support,
            "total_expenses": total_expenses,
            "change_unrestricted": change_unrestricted,
            "change_restricted": change_restricted,
            "change_total": change_total,
            # Perubahan Aset Neto
            "beginning_unrestricted": beginning_unrestricted,
            "beginning_restricted": beginning_restricted,
            "beginning_total": beginning_total,
            # Arus Kas
            "cash_operating": cash_operating,
            "cash_investing": cash_investing,
            "cash_financing": cash_financing,
            "net_cash_flow": net_cash_flow,
            "beginning_cash": beginning_cash,
            "ending_cash": ending_cash,
        }
