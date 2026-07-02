# Nama : Muhammad Ni'am Mawahib
## NIM : A11.2023.15462

# Simple LMS - Technical Documentation

Proyek ini adalah sistem manajemen pembelajaran (LMS) sederhana berbasis Django yang dikelola sepenuhnya menggunakan Docker. Dokumentasi ini merinci arsitektur, konfigurasi, dan langkah-langkah deployment.

## Arsitektur Proyek

Sistem ini menggunakan arsitektur tiga arah (three-tier) yang diisolasi dalam container:

1. **Web App**: Django 4.2 running on Python 3.11-slim.
2. **Database**: PostgreSQL 15 untuk penyimpanan data relasional.
3. **Cache/Broker**: Redis 7 untuk manajemen state dan caching.

## Struktur Direktori

```text
docker-2/
├── docker-compose.yml   # Orchestration services
├── Dockerfile           # Blueprint image Python & Django
├── requirements.txt     # Library dependencies
├── .env                 # Environment variables
└── code/                # Root Source Code (Mapped to /app in container)
    ├── manage.py        # Django Entry Point
    ├── lms/             # Project Core Configuration (settings, urls, wsgi)
    └── courses/         # Application Module (LMS features)
```

## Konfigurasi Environment (`.env`)

Aplikasi membaca variabel berikut untuk koneksi database:

- `DEBUG=True`
- `DATABASE_URL=postgres://postgres:postgres@database:5432/lms_db`
- `REDIS_URL=redis://redis:6379/0`


## Langkah Deployment

### 1. Inisialisasi Container

Membangun image dan menjalankan seluruh service:

```bash
docker-compose up -d --build
```

### 2. Migrasi Skema Database

Menerapkan skema database ke PostgreSQL:

```bash
docker-compose exec app python manage.py migrate
```

### 3. Setup Administrasi

Membuat akun superuser untuk akses panel admin:

```bash
docker-compose exec app python manage.py createsuperuser
```

## Technical Debugging & Fixes

Selama pengembangan, beberapa isu teknis telah diselesaikan:

- **Working Directory Fix**: Menyelaraskan `working_dir` di Docker dengan mapping volume `./code:/app` untuk memastikan `manage.py` terdeteksi.
- **ModuleNotFoundError**: Memastikan keberadaan `__init__.py` di setiap sub-folder module dan memperbaiki typo pada path `BigAutoField`.
- **Container Lifecycle**: Menambahkan `tty: true` dan `stdin_open: true` pada `docker-compose.yml` untuk mencegah container Django exit prematur di lingkungan Windows.

## Perintah Berguna

- **Akses Terminal Container**: `docker-compose exec app bash`
- **Cek Log Real-time**: `docker-compose logs -f app`
- **Hard Reset Volume**: `docker-compose down -v`

---

**Status Proyek**: ✅ Infrastruktur Ready | ✅ Database Connected | ✅ Admin Panel Active
