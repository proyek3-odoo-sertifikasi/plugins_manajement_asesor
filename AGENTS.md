# AGENTS.md — Modul LSP Penugasan Asesor

## 🎯 Project Overview

Modul **`plugins_manajement_asesor`** adalah modul Odoo 19 untuk sistem LSP (Lembaga Sertifikasi Profesi) yang mengelola pemetaan penilaian antara Asesor (penguji) dengan Asesi (peserta ujian) secara otomatis, dengan validasi rasio kuota **maksimal 1 Asesor : 10 Asesi**.

**Version:** `19.0.1.0.0`
**Author:** Tim Manajemen Asesor — D4-3B POLBAN
**License:** LGPL-3

### Dependensi

| Modul | Kegunaan |
|-------|----------|
| `base` | Model dasar Odoo |
| `mail` | Chatter, tracking, notifikasi email |
| `portal` | Portal Asesor (`/my/penugasan`) |
| `plugins_registrasi` | Data asesi (`lsp.student`, state `verified`) |

---

## 🏗️ Arsitektur Modul

### Struktur File (Aktual)

```
plugins_manajement_asesor/
├── __init__.py
├── __manifest__.py
├── AGENTS.md / CONTEXT.md
├── CHANGELOG.md / DEMO_DATA.md / INSTALLATION.md / README.md
│
├── models/
│   ├── __init__.py
│   ├── lsp_jadwal_ujian.py          # Jadwal ujian (dibuat sendiri, blm inherit)
│   ├── lsp_penugasan_asesor.py      # HEADER: satu record per penugasan
│   ├── lsp_penugasan_line.py        # DETAIL: asesor ↔ asesi
│   ├── lsp_slot_waktu.py            # Slot waktu per asesor per ruangan
│   └── lsp_student_inherit.py       # _inherit lsp.student, name_get()
│
├── wizards/
│   ├── __init__.py
│   └── wizard_tambah_asesor.py      # Wizard tambah asesor ke penugasan
│
├── views/
│   ├── lsp_penugasan_asesor_views.xml
│   ├── lsp_penugasan_line_views.xml
│   ├── lsp_jadwal_ujian_views.xml
│   ├── wizard_tambah_asesor_views.xml
│   ├── portal_templates.xml
│   └── menu_views.xml
│
├── security/
│   ├── lsp_penugasan_security.xml   # Groups + record rules
│   └── ir.model.access.csv
│
├── controllers/
│   └── portal_penugasan.py          # Portal routes /my/penugasan
│
├── data/
│   └── lsp_penugasan_data.xml       # Sequence + mail template
│
├── tests/
│   ├── test_penugasan_asesor.py     # 8 test cases
│   └── test_distribusi_otomatis.py  # 5 test cases
│
└── demo/
    └── demo_data.xml
```

### Model Utama

| Model | Type | Keterangan |
|-------|------|------------|
| `lsp.jadwal.ujian` | `_name` (standalone) | Jadwal ujian, state: draft→terjadwal→penugasan→berlangsung→selesai |
| `lsp.penugasan.asesor` | `_name`, `_inherit: mail.thread, mail.activity.mixin` | Header penugasan, state: draft→dikunci |
| `lsp.penugasan.line` | `_name` | Detail asesor ↔ asesi (Many2many ke `lsp.student`) |
| `lsp.slot.waktu` | `_name` | Slot waktu ujian per asesor |
| `lsp.student` | `_inherit` (dari `plugins_registrasi`) | Override `name_get()` → `full_name (NIK)` |

---

## 🔁 Alur Bisnis

```
Admin LSP Pilih Skema & Jadwal Ujian
  → Tambah Asesor (via wizard)
  → Sistem Validasi Kecukupan Asesor (rasio 1:10)
  → Jika cukup: Distribusi Round-Robin Otomatis
  → Admin Kunci Penugasan (Lock)
  → Notifikasi terkirim ke setiap Asesor
  → Asesor cek di Portal /my/penugasan
```

### Aturan Bisnis (BR)

- **BR-01**: 1 Asesor **maks 10 Asesi** per jadwal
- **BR-02**: Sistem blokir jika rasio kapasitas terlampaui
- **BR-03**: Distribusi **round-robin**, otomatis & merata
- **BR-04**: Setelah dikunci, **read-only** (kecuali Admin buka kunci)
- **BR-05**: Notifikasi **wajib** ke setiap Asesor
- **BR-06**: Tidak boleh ada asesor duplikat di jadwal yang sama

---

## ⚙️ Odoo 19 Rules (WAJIB)

### Python
- `from odoo import api, fields, models, _`
- `@api.model_create_multi` untuk override `create()`
- `@api.constrains` di level model (bukan hanya UI)
- `self.ensure_one()` untuk single-record methods
- `ondelete=` eksplisit di semua Many2one
- `copy=False` + `tracking=True` di field `state`
- `_('...')` untuk semua user-facing strings
- Jangan gunakan `@api.one`, `@api.multi`, `self.pool`

### XML Views
- `<list>` bukan `<tree>`
- `invisible="expr"` / `readonly="expr"` — **bukan** `attrs="{}"`
- `<chatter/>` tag tunggal — bukan `<div class="oe_chatter">`
- `<sheet>` wajib di form view
- `states=` deprecated — ganti `invisible=` / `readonly=`

### Security CSV
- Format: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`
- `model_id:id` = `model_` + nama model dengan underscore

---

## 🔗 Integrasi dengan Modul Lain

| Modul | Status | Catatan |
|-------|--------|---------|
| `plugins_registrasi` | ✅ **Done** | `lsp.student` sebagai data asesi |
| `lsp_penjadwalan_ujian` | ⏳ **Pending** | `lsp.jadwal.ujian` perlu `_inherit` |
| `lsp_skema_sertifikasi` | ⏳ **Pending** | `skema_id` perlu Many2one |

---

## ✅ Checklist

**Fungsionalitas Inti:**
- [x] Constraint rasio 1:10 di level model (`_check_max_asesi`)
- [x] SQL constraint unique asesor per penugasan
- [x] Distribusi round-robin, tidak ada >10 per asesor
- [x] Semua asesi tertugaskan setelah distribusi
- [x] State `dikunci` → readonly di view

**Notifikasi & Audit:**
- [x] Notifikasi via mail template + chatter
- [x] `tracking=True` di state

**Keamanan & Akses:**
- [x] `ir.model.access.csv` mencakup semua model
- [x] Record rules: asesor hanya lihat miliknya
- [x] Admin bisa buka kunci, Asesor tidak

**Portal:**
- [x] `/my/penugasan` menampilkan data asesor login
- [x] Detail menampilkan daftar asesi sesuai

**Testing:**
- [x] `test_penugasan_asesor.py` — 8 test cases
- [x] `test_distribusi_otomatis.py` — 5 test cases

---

## 🚫 Larangan

1. Jangan `@api.one` / `@api.multi`
2. Jangan `attrs="{}"` di XML
3. Jangan `<tree>` — pakai `<list>`
4. Jangan `states=` — pakai `invisible=` / `readonly=`
5. Jangan `<div class="oe_chatter">` — pakai `<chatter/>`
6. Jangan `self.pool` — pakai `self.env`
7. Jangan hardcode database ID
8. Jangan `sudo()` tanpa komentar keamanan
9. Jangan `print()` di kode produksi
10. Jangan `@api.model` untuk create — pakai `@api.model_create_multi`

---

*Dokumen ini adalah AGENTS.md untuk modul plugins_manajement_asesor — D4-3B POLBAN 2026*
