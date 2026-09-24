======================================================
Akuntansi Nonlaba & Yayasan Sosial (ISAK 35)
======================================================

.. 
   Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

Modul ini mengimplementasikan standar akuntansi keuangan resmi Indonesia untuk entitas berorientasi
nonlaba, yayasan, panti sosial, dan Lembaga Kesejahteraan Sosial (LKS) berdasarkan
Interpretasi Standar Akuntansi Keuangan 35 (ISAK 35) yang diterbitkan oleh Dewan Standar Akuntansi
Keuangan Ikatan Akuntan Indonesia (DSAK IAI), menggantikan PSAK 45 yang telah dicabut.

Fitur Utama
===========
* **Bagan Akun Standar (COA) Nonlaba / Yayasan**:
  - Klasifikasi Aset Neto Tanpa Pembatasan (Unrestricted Net Assets).
  - Klasifikasi Aset Neto Dengan Pembatasan (Restricted Net Assets) untuk hibah terikat Kemensos, APBN/APBD, atau donor institusi/CSR.
  - Akun beban program terpisah menurut kluster sosial (Beban Permakanan/Gizi, Beban Pendidikan, Beban Kesehatan, Beban Bimbingan Mental & Vokasional, Beban Bantuan Keluarga).
  - Akun beban pendukung terpisah (Manajemen, Umum, dan Penggalangan Dana).
  - Mekanisme pelepasan pembatasan (Aset Neto Terbebaskan dari Pembatasan).
* **4 Laporan Keuangan Wajib ISAK 35 (Wizard & Engine Dinamis)**:
  1. **Laporan Posisi Keuangan (Statement of Financial Position)**:
     Menyajikan Aset Lancar, Aset Tidak Lancar, Liabilitas Jangka Pendek & Panjang, serta Aset Neto Tanpa Pembatasan vs Dengan Pembatasan.
  2. **Laporan Penghasilan Komprehensif / Aktivitas (Statement of Activities)**:
     Menyajikan pendapatan, sumbangan, pelepasan aset neto, beban program vs beban pendukung, serta kenaikan/(penurunan) aset neto periode berjalan.
  3. **Laporan Perubahan Aset Neto (Statement of Changes in Net Assets)**:
     Rekonsiliasi saldo awal aset neto, surplus/defisit berjalan, reklasifikasi, dan saldo akhir aset neto.
  4. **Laporan Arus Kas (Statement of Cash Flows)**:
     Arus kas dari Aktivitas Operasi, Aktivitas Investasi, dan Aktivitas Pendanaan.
* **Cetak Laporan QWeb PDF**:
  Format resmi dengan kop yayasan, pemisahan kolom Tanpa Pembatasan dan Dengan Pembatasan, serta tanda tangan Ketua Yayasan dan Bendahara.

Instalasi & Dependensi
======================
* Dependensi: ``account``, ``base``, ``mail``
* Versi Odoo: 18.0 LTS & 19.0 Community Edition
