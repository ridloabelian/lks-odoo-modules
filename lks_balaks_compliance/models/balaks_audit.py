# Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LksBalaksAudit(models.Model):
    _name = "lks.balaks.audit"
    _description = "Sesi Audit & Simulasi Akreditasi BALAKS Kemensos"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "audit_date desc, id desc"

    name = fields.Char(
        string="Nama Sesi Audit",
        required=True,
        tracking=True,
        help="Contoh: Audit Kesiapan Akreditasi BALAKS Tahun 2026",
    )
    audit_date = fields.Date(
        string="Tanggal Pelaksanaan Audit",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    auditor_id = fields.Many2one(
        comodel_name="res.users",
        string="Ketua Tim Asesor / Audit Internal",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    target_cluster = fields.Selection(
        selection=[
            ("anak", "Kluster LKS Anak (Panti Asuhan)"),
            ("lansia", "Kluster LKS Lansia (Panti Wreda)"),
            ("disabilitas", "Kluster LKS Disabilitas"),
            ("tunasosial", "Kluster LKS Tuna Sosial & Napza"),
            ("all", "Semua Kluster Terpadu"),
        ],
        string="Kluster Layanan Sasaran",
        default="anak",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="lks.balaks.audit.line",
        inverse_name="audit_id",
        string="Rincian Penilaian Indikator",
        copy=True,
    )

    # -------------------------------------------------------------------------
    # SKOR & PREDIKSI AKREDITASI
    # -------------------------------------------------------------------------
    total_score = fields.Float(
        string="Total Skor Akreditasi (0 - 100)",
        compute="_compute_scores",
        store=True,
        tracking=True,
        help="Skor terbobot total dari 6 standar nasional BALAKS Kemensos.",
    )
    accreditation_prediction = fields.Selection(
        selection=[
            ("A", "Akreditasi A (Sangat Baik / Terakreditasi Unggul)"),
            ("B", "Akreditasi B (Baik)"),
            ("C", "Akreditasi C (Cukup)"),
            ("unaccredited", "Tidak Terakreditasi (Belum Memenuhi Standar Minimal)"),
        ],
        string="Prediksi Peringkat Akreditasi",
        compute="_compute_scores",
        store=True,
        tracking=True,
    )
    evidence_completeness_rate = fields.Float(
        string="Kelengkapan Dokumen Eviden (%)",
        compute="_compute_scores",
        store=True,
    )
    recommendations = fields.Text(
        string="Catatan & Rencana Tindak Lanjut Perbaikan",
        help="Langkah-langkah pemenuhan eviden sebelum visitasi resmi asesor BALAKS Kemensos.",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft Persiapan"),
            ("in_progress", "Proses Asesmen / Visitasi"),
            ("completed", "Selesai Dievaluasi"),
            ("cancel", "Dibatalkan"),
        ],
        string="Status Audit",
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

    @api.depends("line_ids.score_obtained", "line_ids.evidence_status")
    def _compute_scores(self):
        for rec in self:
            if not rec.line_ids:
                rec.total_score = 0.0
                rec.accreditation_prediction = "unaccredited"
                rec.evidence_completeness_rate = 0.0
                continue

            # Hitung skor terbobot per standar
            standard_scores = {}
            standard_max = {}
            complete_count = 0

            for line in rec.line_ids:
                std_id = line.standard_id.id
                if std_id not in standard_scores:
                    standard_scores[std_id] = 0.0
                    standard_max[std_id] = 0.0
                standard_scores[std_id] += line.score_obtained
                standard_max[std_id] += line.max_score
                if line.evidence_status == "complete":
                    complete_count += 1

            total_weighted = 0.0
            for std in self.env["lks.balaks.standard"].search([]):
                if std.id in standard_max and standard_max[std.id] > 0:
                    pct = standard_scores[std.id] / standard_max[std.id]
                    total_weighted += (pct * std.weight)

            rec.total_score = round(total_weighted, 2)
            rec.evidence_completeness_rate = round((complete_count / len(rec.line_ids)) * 100.0, 1) if rec.line_ids else 0.0

            # Klasifikasi Peringkat
            if rec.total_score >= 86.0:
                rec.accreditation_prediction = "A"
            elif rec.total_score >= 71.0:
                rec.accreditation_prediction = "B"
            elif rec.total_score >= 56.0:
                rec.accreditation_prediction = "C"
            else:
                rec.accreditation_prediction = "unaccredited"

    def action_load_indicators(self):
        """Memuat seluruh indikator dari master 6 standar BALAKS secara otomatis."""
        self.ensure_one()
        indicators = self.env["lks.balaks.indicator"].search([], order="standard_id, sequence")
        lines = []
        for ind in indicators:
            lines.append((0, 0, {
                "indicator_id": ind.id,
                "standard_id": ind.standard_id.id,
                "max_score": ind.max_score,
                "score_obtained": ind.max_score * 0.8,  # baseline estimasi
                "evidence_status": "partial",
            }))
        self.line_ids = [(5, 0, 0)] + lines

    def action_start(self):
        for rec in self:
            rec.state = "in_progress"

    def action_complete(self):
        for rec in self:
            rec.state = "completed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    def action_set_to_draft(self):
        for rec in self:
            rec.state = "draft"


class LksBalaksAuditLine(models.Model):
    _name = "lks.balaks.audit.line"
    _description = "Rincian Penilaian Indikator Audit BALAKS"
    _order = "standard_id asc, id asc"

    audit_id = fields.Many2one(
        comodel_name="lks.balaks.audit",
        string="Sesi Audit",
        required=True,
        ondelete="cascade",
    )
    indicator_id = fields.Many2one(
        comodel_name="lks.balaks.indicator",
        string="Indikator Akreditasi",
        required=True,
    )
    standard_id = fields.Many2one(
        comodel_name="lks.balaks.standard",
        string="Standar Nasional",
        related="indicator_id.standard_id",
        store=True,
        readonly=True,
    )
    max_score = fields.Float(
        string="Skor Maksimal",
        related="indicator_id.max_score",
        readonly=True,
    )
    score_obtained = fields.Float(
        string="Skor Diperoleh",
        default=0.0,
        required=True,
    )
    evidence_status = fields.Selection(
        selection=[
            ("complete", "Dokumen Eviden Lengkap & Valid"),
            ("partial", "Eviden Sebagian / Perlu Perbaikan"),
            ("missing", "Belum Ada Dokumen Eviden"),
        ],
        string="Status Kelengkapan Eviden",
        default="missing",
        required=True,
    )
    notes = fields.Char(
        string="Catatan Asesor / Temuan Lapangan",
    )
    evidence_file = fields.Binary(
        string="Unggah Berkas Eviden",
        attachment=True,
    )
    evidence_filename = fields.Char(
        string="Nama File Eviden",
    )

    @api.constrains("score_obtained", "max_score")
    def _check_score(self):
        for rec in self:
            if rec.score_obtained > rec.max_score or rec.score_obtained < 0:
                raise ValidationError(
                    _(
                        "Skor yang diperoleh (%(score).2f) tidak boleh melebihi skor maksimal (%(max).2f) atau bernilai negatif!"
                    )
                    % {"score": rec.score_obtained, "max": rec.max_score}
                )
