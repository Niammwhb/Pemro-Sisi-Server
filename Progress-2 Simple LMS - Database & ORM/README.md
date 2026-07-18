# 🎓 Simple LMS - Database Design & ORM Implementation

Implementasi **Database Design & Django ORM** pada aplikasi **Simple Learning Management System (LMS)** menggunakan Django dan PostgreSQL.

---

# 👨‍💻 Author

**Nama** : Muhammad Ni'am Mawahib
**NIM** : A11.2023.15462

---

# 📖 Deskripsi Project

Project ini merupakan implementasi **Database Design & ORM** pada aplikasi **Simple Learning Management System (LMS)**.

Fokus utama project adalah mendesain struktur database yang baik menggunakan **Django ORM**, mengimplementasikan berbagai jenis relasi antar model, melakukan optimasi query menggunakan **select_related()** dan **prefetch_related()**, serta memanfaatkan **Django Admin** sebagai media pengelolaan data.

Database yang digunakan adalah **PostgreSQL** dan aplikasi dijalankan menggunakan **Docker Compose**.

---

# 🎯 Learning Objectives

Project ini bertujuan untuk:

- Mendesain database schema untuk Learning Management System
- Mengimplementasikan Django Models menggunakan ORM
- Menggunakan berbagai jenis relationship pada Django
- Mengoptimalkan performa query database
- Menggunakan Django Admin Interface
- Membuat Custom Model Manager
- Menggunakan Migration dan Initial Fixtures

---

# 🛠️ Teknologi yang Digunakan

- Python 3.12
- Django 5.x
- PostgreSQL
- Django ORM
- Docker
- Docker Compose

---

# 📁 Struktur Project

```text
Progress-2 Simple LMS - Database & ORM

│
├── code
│   ├── courses
│   ├── lms
│   ├── manage.py
│   └── db.sqlite3
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🗄️ Database Schema

Project memiliki beberapa model utama sebagai berikut.

## 1. User

Role yang tersedia:

- Admin
- Instructor
- Student

Relationship

```
User
│
├── Course
└── Enrollment
```

---

## 2. Category

Category menggunakan **Self Referencing ForeignKey** sehingga dapat membentuk kategori bertingkat.

Contoh:

```
Programming
│
├── Python
├── Java
└── Web Development
```

---

## 3. Course

Setiap Course memiliki:

- Instructor
- Category

Relationship

```
Instructor
      │
   Course
      │
   Category
```

---

## 4. Lesson

Lesson berada di dalam Course.

Ordering menggunakan

```python
ordering = ["order"]
```

Sehingga seluruh lesson akan tampil sesuai urutan.

---

## 5. Enrollment

Enrollment menyimpan data student yang mengambil course.

Relationship

```
Student
    │
Enrollment
    │
Course
```

Menggunakan **Unique Constraint**

```
(student, course)
```

agar student tidak dapat melakukan enrollment dua kali pada course yang sama.

---

## 6. Progress

Progress digunakan untuk mencatat penyelesaian lesson oleh student.

Relationship

```
Enrollment
      │
 Progress
      │
 Lesson
```

---

# 🔗 Relasi Antar Model

| Model                 | Relationship     |
| --------------------- | ---------------- |
| User → Course         | One To Many      |
| User → Enrollment     | One To Many      |
| Category → Category   | Self Referencing |
| Category → Course     | One To Many      |
| Course → Lesson       | One To Many      |
| Course → Enrollment   | One To Many      |
| Enrollment → Progress | One To Many      |
| Lesson → Progress     | One To Many      |

---

# ⚙️ Custom Model Managers

## Course Manager

```python
Course.objects.for_listing()
```

Menggunakan

```python
select_related("category", "instructor")
.prefetch_related("lessons")
```

Fungsi:

- Optimasi halaman daftar Course
- Mengurangi jumlah query database
- Menghindari N+1 Query Problem

---

## Enrollment Manager

```python
Enrollment.objects.for_student_dashboard()
```

Menggunakan

```python
select_related("student", "course")
.prefetch_related("progress_set")
```

Digunakan untuk menampilkan dashboard student secara lebih efisien.

---

# 🚀 Query Optimization

## Tanpa Optimasi

```python
courses = Course.objects.all()

for course in courses:
    print(course.instructor.username)
```

Misal terdapat **100 Course**

Jumlah query

```
1 Query Course

100 Query Instructor

Total = 101 Query
```

---

## Menggunakan select_related()

```python
Course.objects.select_related(
    "instructor",
    "category"
)
```

Jumlah query

```
1 Query
```

---

## Menggunakan prefetch_related()

```python
Course.objects.prefetch_related(
    "lessons"
)
```

Semua lesson akan diambil sekaligus sehingga query menjadi jauh lebih efisien.

---

# 🖥️ Django Admin

Project memanfaatkan Django Admin untuk memudahkan pengelolaan data.

Fitur yang tersedia:

- Search
- Filter
- Ordering
- List Display
- Inline Lesson

### User Admin

- Username
- Email
- Role

### Course Admin

- Title
- Instructor
- Category

### Enrollment Admin

- Student
- Course
- Enrolled At

### Progress Admin

- Student
- Lesson
- Completed
- Completed At

---

# 📦 Migration

Membuat migration

```bash
python manage.py makemigrations
```

Menjalankan migration

```bash
python manage.py migrate
```

---

# 📂 Initial Data Fixtures

Load initial data

```bash
python manage.py loaddata initial_data.json
```

Data yang tersedia:

- Admin
- Instructor
- Student
- Category
- Course
- Lesson
- Enrollment

---

# Menjalankan Project

## Clone Repository

```bash
git clone <repository-url>
```

Masuk ke folder project

```bash
cd Progress-2-Simple-LMS
```

Build Docker

```bash
docker compose build
```

Menjalankan Container

```bash
docker compose up -d
```

Menjalankan Migration

```bash
docker compose exec web python manage.py migrate
```

Membuat Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

Load Fixtures

```bash
docker compose exec web python manage.py loaddata initial_data.json
```

---

# 🌐 URL Aplikasi

| Service      | URL                         |
| ------------ | --------------------------- |
| Django       | http://localhost:8000       |
| Django Admin | http://localhost:8000/admin |

---

# 📚 Kesimpulan

Project **Simple LMS – Database Design & ORM Implementation** berhasil mengimplementasikan desain database menggunakan **Django ORM** dengan relasi yang sesuai kebutuhan Learning Management System.

Selain mendukung berbagai jenis relasi model, project ini juga menerapkan optimasi query menggunakan **select_related()** dan **prefetch_related()** untuk mengurangi jumlah query database dan meningkatkan performa aplikasi. Konfigurasi **Django Admin**, **Custom Model Manager**, **Migration**, dan **Initial Data Fixtures** juga telah diimplementasikan sehingga aplikasi mudah dikelola dan siap dikembangkan lebih lanjut.

---

# 📄 License

Project ini dibuat sebagai tugas mata kuliah **Pemrograman Sisi Server** di **Universitas Dian Nuswantoro**.
