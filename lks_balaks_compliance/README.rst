==============================================================
Kepatuhan Akreditasi LKS & Ekspor SIKS-NG Kemensos
==============================================================

.. 
   Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

Modul kesiapan audit akreditasi Lembaga Kesejahteraan Sosial (LKS) berdasarkan 6 Standar
Nasional Badan Akreditasi Lembaga Kesejahteraan Sosial (BALAKS Kemensos RI) dan integrasi
ekspor data binaan format Dinas Sosial serta SIKS-NG Kemensos RI.

Fitur Utama
===========
* **6 Standar Nasional Akreditasi BALAKS Kemensos**:
  1. *Standar Program*: Kesesuaian program dengan PPKS, legalitas badan hukum Kemenkumham, Tanda Daftar & Izin Operasional Dinsos.
  2. *Standar Proses Pelayanan*: 7 tahapan Case Management (Intake, Asesmen Komprehensif, Case Plan, 4 Pilar Intervensi, Evaluasi, Terminasi, Aftercare).
  3. *Standar Manajemen Organisasi*: Struktur organisasi, SOP pelayanan lengkap, pembukuan transparan berstandar ISAK 35.
  4. *Standar SDM / Pekerja Sosial*: Kualifikasi S1 Kesos, STR Sakti Peksos Kemensos, rasio pendamping terhadap klien binaan (1 : 15 s/d 1 : 20).
  5. *Standar Sarana dan Prasarana*: Kelaikan asrama tempat tinggal, ruang konseling psikososial tertutup, sanitasi MCK sehat, proteksi kebakaran APAR.
  6. *Standar Hasil Layanan (Outcome)*: Persentase keberhasilan reunifikasi keluarga, kelulusan sekolah/mandiri kerja, kepuasan penerima manfaat.
* **Audit & Simulasi Kesiapan Akreditasi**:
  - Penilaian indikator mandiri (Self-Assessment) dengan skor terbobot 0 - 100 poin.
  - Prediksi peringkat akreditasi otomatis:
    * Skor >= 86.00: **Akreditasi A (Sangat Baik / Unggul)**
    * Skor 71.00 - 85.99: **Akreditasi B (Baik)**
    * Skor 56.00 - 70.99: **Akreditasi C (Cukup)**
    * Skor < 56.00: **Tidak Terakreditasi**
  - Matriks eviden dokumen digital per indikator dan tingkat kelengkapan dokumen (%).
  - Catatan rekomendasi pemenuhan dokumen sebelum kedatangan Tim Asesor Kemensos.
* **Profil Lembaga & Perizinan LKS**:
  - Rekam data legalitas: Tanda Daftar Dinsos, Izin Operasional, SK Kemenkumham, NIB OSS, Sertifikat Akreditasi.
  - Otomasi rasio Pekerja Sosial bersertifikat terhadap jumlah klien asuhan aktif.
* **Ekspor Data Binaan Format SIKS-NG Kemensos & Dinas Sosial**:
  - Wizard ekspor CSV (UTF-8 BOM) sesuai standar kolom impor SIKS-NG (34 kolom lengkap: NIK, No. KK, Alamat Kemendagri, Kluster PPKS, Wali, Peksos Pendamping).
  - Filter kluster PPKS, status residensial (dalam panti / luar panti), dan status layanan.
* **Laporan Cetak QWeb PDF**:
  - Lembar Hasil Evaluasi Audit Kesiapan Akreditasi BALAKS Kemensos.
  - Laporan Profil Kelembagaan LKS & Rekapitulasi Pelayanan PPKS untuk Dinas Sosial.

Instalasi & Dependensi
======================
* Dependensi: ``lks_core``, ``lks_social_care``, ``l10n_id_nonprofit_isak35``
* Versi Odoo: 18.0 LTS & 19.0 Community Edition
