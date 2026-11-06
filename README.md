# School Management System (Backend)

A production-ready Modular Monolith backend for a School Management System built using **FastAPI**, **SQLAlchemy 2.0 (asyncpg)**, **Alembic**, and **PostgreSQL (Neon.tech)**.

---

## Stack

- **Python 3.12**
- **FastAPI**
- **SQLAlchemy 2.0** with `asyncpg` async driver
- **Alembic** for asynchronous database migrations
- **Pydantic v2** & **pydantic-settings**
- **passlib[bcrypt]** for secure password hashing
- **PyJWT** for JSON Web Tokens
- **PostgreSQL on Neon.tech** (Serverless with connection pooling)
- **pytest**, **pytest-asyncio**, and **httpx** for comprehensive automated testing

---

## Directory Structure

```text
school-management/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   ├── config.py
│   │
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │
│   ├── modules/
│   │   ├── auth/          # Authentication & JWT tokens
│   │   ├── users/         # User accounts & RBAC
│   │   ├── students/      # Student profiles & report cards
│   │   ├── teachers/      # Teacher profiles & assignments
│   │   ├── classes/       # Classes, enrollments, subject assignments
│   │   ├── subjects/      # Subjects & courses
│   │   ├── attendance/    # Session attendance tracking
│   │   ├── exams/         # Exams, grading rules, and results
│   │   ├── fees/          # Fee invoices, payments & dynamic balance
│   │   ├── guardian/      # Guardian portal orchestration
│   │   ├── reports/       # Admin dashboards and financial summaries
│   │   └── audit/         # Transactional audit logs
│   │
│   ├── tests/
│   ├── seed.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   └── architecture.md
│
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Set Up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `backend/.env` and update the database password from Neon:
```bash
cp backend/.env.example backend/.env
```
Ensure `backend/.env` contains your Neon pooled and direct connection strings:
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:<YOUR_PASSWORD>@ep-late-grass-az9n8r4l-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?ssl=require
DATABASE_URL_DIRECT=postgresql+asyncpg://neondb_owner:<YOUR_PASSWORD>@ep-late-grass-az9n8r4l.c-3.ap-southeast-1.aws.neon.tech/neondb?ssl=require
SECRET_KEY=32-length-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=development
```

### 3. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 4. Run Seed Data
```bash
python seed.py
```

### 5. Start the Server
```bash
uvicorn main:app --reload --port 8000
```
Open interactive Swagger docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Demo Accounts

All accounts are pre-seeded and idempotent:

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@school.demo` | `Admin@123` | Full access to all modules and reports |
| **Teacher** | `teacher.a@school.demo` | `Teacher@123` | Amit Verma (`TCH001`), teaches Class 10A (Maths & Science) |
| **Teacher** | `teacher.b@school.demo` | `Teacher@123` | Sunita Rao (`TCH002`), teaches Class 10B (English) |
| **Guardian** | `guardian.a@school.demo` | `Guardian@123` | Guardian of Ravi Sharma, Arjun Singh, Rahul Das |
| **Guardian** | `guardian.b@school.demo` | `Guardian@123` | Guardian of Priya Mehta, Sneha Patel |

---

## Running Automated Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

