==============================================================
LKS & Panti Sosial - Manajemen Asuhan & Case Management PPKS
==============================================================

.. 
   Copyright 2026 Lembaga Kesejahteraan Sosial (LKS) Indonesia
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

Modul Case Management dan pemantauan perkembangan individu Pemerlu Pelayanan
Kesejahteraan Sosial (PPKS) untuk Lembaga Kesejahteraan Sosial (LKS) dan Panti Asuhan/Wreda.

Fitur Utama
===========
* **Monitoring Perkembangan Pendidikan**:
  - Jenjang PAUD, TK, SD/MI, SMP/MTs, SMA/SMK, SLB, Pesantren, hingga Perguruan Tinggi/Vokasional.
  - Pencatatan NISN, nama sekolah, kelas, tahun ajaran, dan sumber beasiswa (KIP/PIP, BOS, Orang Tua Asuh, Subsidi Yayasan).
  - Evaluasi buku rapor per semester (nilai rata-rata, ranking, sikap/perilaku, prestasi, file scan rapor).
  - Manajemen kelulusan dan penyimpanan arsip digital ijazah.
* **Rekam Medis & Kesehatan Dasar Panti**:
  - Profil kesehatan klien: Golongan darah, rhesus, riwayat alergi makanan/obat, penyakit kronis/bawaan, kebutuhan alat bantu.
  - Kartu KIS / BPJS Kesehatan PBI APBN/APBD dan Faskes 1 terdaftar.
  - Riwayat imunisasi lengkap (BCG, DPT, Polio, Campak, COVID-19, dll.).
  - Log kunjungan berobat ke Puskesmas, Rumah Sakit, Posyandu, atau Ruang Kesehatan Panti.
  - Pemantauan berkala tanda vital dan Indeks Massa Tubuh (IMT / Status Gizi).
* **Rencana Intervensi Layanan Individual (Case Plan)**:
  - Identifikasi masalah kerentanan, kekuatan klien, target capaian jangka pendek dan jangka panjang.
  - 4 Pilar Intervensi Sosial: Bimbingan Fisik, Mental Spiritual, Sosial Psikologis, dan Pelatihan Vokasional.
  - Integrasi tombol aksi ke modul ``npo_assessment`` untuk asesmen desil kemiskinan.
  - Integrasi tombol aksi ke modul ``npo_disbursement_base`` untuk pengajuan bantuan dan pencairan manfaat.
* **Terminasi & Penyatuan Kembali (Reunifikasi) Keluarga**:
  - Bentuk terminasi: Reuni keluarga kandung, adopsi resmi penetapan pengadilan, kemandirian kerja, rujukan balai.
  - Asesmen kesiapan keluarga (Home Visit) dan kesiapan emosional klien.
  - Rencana bimbingan lanjut (Aftercare) berkala 1 bulan, 3 bulan, dan 6 bulan.
  - Pengubahan otomatis status layanan klien menjadi terminasi / keluar.
* **Laporan Cetak QWeb PDF**:
  - Rapor Perkembangan Layanan Individual (Case Plan Summary).
  - Resume Rekam Medis & Riwayat Kesehatan Klien.
  - Berita Acara Serah Terima (BAST) Reuni Keluarga & Terminasi Resmi Sakti Peksos.

Instalasi & Dependensi
======================
* Dependensi: ``lks_core``, ``npo_assessment``, ``npo_disbursement_base``
* Versi Odoo: 18.0 LTS & 19.0 Community Edition
