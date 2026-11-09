# School Management System

A production-ready, full-stack School Management System featuring a **FastAPI** modular monolith backend and a **React + Vite + TypeScript + Tailwind CSS** frontend with dedicated role-based portals for **Admins**, **Teachers**, and **Guardians**.

---

## 🌐 Live Deployments

- **Web Application**: [https://sms-portal-fawn.vercel.app](https://sms-portal-fawn.vercel.app) (Hosted on Vercel)
- **Backend API & Swagger Docs**: [https://sms-9x94.onrender.com/docs](https://sms-9x94.onrender.com/docs) (Hosted on Render)
- **Database**: PostgreSQL on [Neon.tech](https://neon.tech) (Serverless with pooling)

> [!IMPORTANT]
> **Live Demo First Load (Render Cold-Start)**: The backend API is hosted on Render's free tier. If the service has been idle, Render automatically spins down the container. **Please wait 30–45 seconds on your first page load or login attempt** while Render wakes up the backend. Once active, all subsequent requests, queries, and role transitions will respond with instant low latency.

---

## Tech Stack

### Backend
- **Python 3.12** & **FastAPI**
- **SQLAlchemy 2.0** with `asyncpg` async driver
- **Alembic** for database schema migrations
- **Pydantic v2** & **pydantic-settings**
- **passlib[bcrypt]** & **PyJWT** for authentication and RBAC
- **PostgreSQL (Neon.tech)** (Serverless with connection pooling)
- **pytest**, **pytest-asyncio**, and **httpx** for test coverage (34 test cases)

### Frontend
- **React 18** & **Vite 5**
- **TypeScript** (Strict Mode, 0 `any` types)
- **Tailwind CSS v3**
- **shadcn/ui** and Base UI accessible primitives
- **React Router v6**
- **Axios** with authenticated request/response interceptors

---

## Portals & Features

1. **Admin Portal**
   - **Dashboard**: High-level statistics (students, teachers, classes, attendance rate, outstanding fees, recent audit logs).
   - **Students & Teachers**: Full CRUD management with search, filtering, and guardian linkage.
   - **Classes & Subjects**: Class sections, course codes, and teacher subject assignments.
   - **Attendance Management**: Class-wide attendance records, date filtering, and status updates.
   - **Exams & Grading Rules**: Create exams, define custom grading scales, and review student grades.
   - **Fees Management**: Generate invoices, record partial or full payments, and track balances.
   - **Audit Logs**: Immutable transactional tracking of all administrative operations.

2. **Teacher Portal**
   - **Dashboard & My Classes**: View assigned sections and enrolled student rosters.
   - **Mark Attendance**: Daily class attendance entry (present, absent, late).
   - **Enter Exam Results**: Enter and edit marks with real-time automatic grading rule application.

3. **Guardian Portal**
   - **Student Profiles**: Overview of enrolled children.
   - **Attendance History**: Date-range filtered attendance rates and session logs.
   - **Academic Report Cards**: Aggregated performance, total marks, and subject grades.
   - **Fees & Ledger**: Live invoice tracking, payments made, and outstanding balance breakdown.

---

## Directory Structure

```text
school-management-system/
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── database.py            # Async engine and session factory
│   ├── dependencies.py        # RBAC guards & session injection
│   ├── config.py              # Environment configuration
│   ├── seed.py                # Idempotent database seeder
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env.example
│   ├── migrations/            # Alembic async migration versions
│   ├── modules/               # Domain modules (auth, users, students, teachers, etc.)
│   └── tests/                 # Automated test suite (34 tests)
│
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── tailwind.config.js
│   └── src/
│       ├── main.tsx           # React entry point
│       ├── App.tsx            # Routes and role protection
│       ├── types/             # Shared TypeScript interfaces
│       ├── api/               # Axios API client services
│       ├── context/           # AuthContext & token management
│       ├── components/        # Layout, DataTable, Spinner, Badges, Modals
│       ├── pages/
│       │   ├── Login.tsx
│       │   ├── admin/         # Admin portal views
│       │   ├── teacher/       # Teacher portal views
│       │   └── guardian/      # Guardian portal views
│       └── utils/             # Helpers & error extractors
│
├── .github/
│   └── workflows/
│       └── ci.yml             # Dual-job CI (Backend Pytest + Frontend TypeScript/Build)
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** & **npm**
- **PostgreSQL** instance (or free Neon.tech serverless database)

---

### Backend Setup

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   ```
   Update `backend/.env` with your PostgreSQL database connection strings:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:6543/dbname?sslmode=require
   DATABASE_URL_DIRECT=postgresql+asyncpg://user:password@host:5432/dbname?sslmode=require
   SECRET_KEY=your-secret-key-minimum-32-characters
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ENVIRONMENT=development
   ```

3. **Run database migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Seed demo data:**
   ```bash
   python seed.py
   ```

5. **Start the backend server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Backend API & Swagger Docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the frontend development server:**
   ```bash
   npm run dev
   ```
   Access the web application at [http://localhost:5173](http://localhost:5173).

---

### Quick Start with Docker (Recommended)

To run the entire full-stack system in isolated production containers:

1. **Ensure `backend/.env` is configured with your database string:**
   ```bash
   cp backend/.env.example backend/.env
   # Update DATABASE_URL in backend/.env
   ```

2. **Build and launch both containers:**
   ```bash
   docker compose up --build
   ```

3. **Access the application:**
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Demo Accounts

> [!TIP]
> **First Login**: If logging in for the first time or after a period of inactivity, please wait **30–45 seconds** for Render to spin up the sleeping backend service before retrying.

All credentials are created automatically by `seed.py` with 12 students across 3 classes, 3 teachers, and 5 guardians:

| Role | Email | Password | Access Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@school.demo` | `Admin@123` | System Administrator (Full control across all modules) |
| **Teacher** | `teacher.a@school.demo` | `Teacher@123` | Amit Verma (`TCH001`), Class 10A & 11A (Mathematics & Science) |
| **Teacher** | `teacher.b@school.demo` | `Teacher@123` | Sunita Rao (`TCH002`), Class 10B & 11A (English) |
| **Teacher** | `teacher.c@school.demo` | `Teacher@123` | Ramesh Gupta (`TCH003`), Class 10A & 10B (History) |
| **Guardian** | `guardian.a@school.demo` | `Guardian@123` | Rajesh Sharma (Guardian of Ravi Sharma, Arjun Singh, Rahul Das) |
| **Guardian** | `guardian.b@school.demo` | `Guardian@123` | Vikram Mehta (Guardian of Priya Mehta, Sneha Patel) |
| **Guardian** | `guardian.c@school.demo` | `Guardian@123` | Sanjay Verma (Guardian of Aditi Verma, Rohan Verma) |
| **Guardian** | `guardian.d@school.demo` | `Guardian@123` | Anil Kapoor (Guardian of Kavya Kapoor, Vihaan Kapoor, Ananya Kapoor) |
| **Guardian** | `guardian.e@school.demo` | `Guardian@123` | Sunil Joshi (Guardian of Ishaan Joshi, Diya Joshi) |

### Demo Student Roster (12 Students)

| Roll No | Student Name | Class | Guardian | Fee Status |
| :--- | :--- | :--- | :--- | :--- |
| `STU001` | Ravi Sharma | Class 10-A | Rajesh Sharma (`guardian.a@school.demo`) | Partial (₹3,000 due) |
| `STU002` | Priya Mehta | Class 10-B | Vikram Mehta (`guardian.b@school.demo`) | Paid (₹0 due) |
| `STU003` | Arjun Singh | Class 10-A | Rajesh Sharma (`guardian.a@school.demo`) | No Invoice |
| `STU004` | Sneha Patel | Class 10-B | Vikram Mehta (`guardian.b@school.demo`) | No Invoice |
| `STU005` | Rahul Das | Class 10-A | Rajesh Sharma (`guardian.a@school.demo`) | Unpaid (₹5,000 due) |
| `STU006` | Aditi Verma | Class 10-A | Sanjay Verma (`guardian.c@school.demo`) | Partial (₹2,500 due) |
| `STU007` | Rohan Verma | Class 10-B | Sanjay Verma (`guardian.c@school.demo`) | No Invoice |
| `STU008` | Kavya Kapoor | Class 10-A | Anil Kapoor (`guardian.d@school.demo`) | Paid (₹0 due) |
| `STU009` | Vihaan Kapoor | Class 10-B | Anil Kapoor (`guardian.d@school.demo`) | No Invoice |
| `STU010` | Ananya Kapoor | Class 11-A | Anil Kapoor (`guardian.d@school.demo`) | Partial (₹3,000 due) |
| `STU011` | Ishaan Joshi | Class 11-A | Sunil Joshi (`guardian.e@school.demo`) | Unpaid (₹6,000 due) |
| `STU012` | Diya Joshi | Class 11-A | Sunil Joshi (`guardian.e@school.demo`) | No Invoice |

---

## Automated Testing & CI

### Running Backend Tests
```bash
cd backend
pytest tests/ -v --tb=short
```

### Running Frontend Checks
```bash
cd frontend
# 1. Typecheck
npx tsc --noEmit

# 2. Linting
npm run lint

# 3. Production Build
npm run build
```

### Continuous Integration (GitHub Actions)
The repository uses [ci.yml](.github/workflows/ci.yml) to run on every push and pull request to `main`:
1. **Backend Job**: Spins up a PostgreSQL 16 service container, applies Alembic migrations, and executes the 34-test Pytest suite.
2. **Frontend Job**: Sets up Node.js 20, verifies TypeScript compilation (`tsc --noEmit`), runs ESLint, and creates a production build.
