# Architecture Documentation: School Management System

## 1. Architectural Pattern: Modular Monolith

The School Management System backend is structured as a **Modular Monolith** in FastAPI. It is deployed as a single, unified backend application while maintaining strict internal boundaries between domain modules.

### Core Architectural Principles:
1. **Module Self-Containment**:
   Every domain module owns its own:
   - `model.py` (SQLAlchemy 2.0 declarative models)
   - `schemas.py` (Pydantic v2 validation contracts)
   - `service.py` (Domain business logic and database queries)
   - `router.py` (FastAPI route controllers)
2. **Zero Direct Cross-Module Model Imports**:
   No module ever imports another module's SQLAlchemy model class. All cross-domain queries and validations go exclusively through public `service.py` functions.
3. **Audit-Driven Transactions**:
   All state-altering actions (creation, updates, deactivations, attendance marks, grading, and fee payments) write audit logs inside the **exact same database transaction**. If an audit log entry fails, the primary operation is automatically rolled back.

---

## 2. Domain Modules Overview

| Module | Responsibilities | Key Rules & Constraints |
| :--- | :--- | :--- |
| **`auth`** | Token generation, verification, and credentials validation | JWT (HS256), passlib bcrypt hashing, generic 401 error messages |
| **`users`** | Identity, authentication records, and roles (admin, teacher, guardian) | Unique emails, soft deletes (`is_active=False`) |
| **`students`** | Student profiles and report card aggregation | Unique `roll_number`, linked to guardian user |
| **`teachers`** | Teacher employee profiles linked to user accounts | Unique `employee_code`, atomic user+teacher creation |
| **`classes`** | Academic classes, class enrollment, subject-teacher assignments | Unique `(name, section, academic_year)`, enrollment & assignment constraints |
| **`subjects`** | School courses and maximum marks | Unique `code`, marks thresholds |
| **`attendance`**| Daily session attendance tracking | Unique `(student_id, date, session)`, teacher assignment verification, enrolled verification |
| **`exams`** | Exam definitions, grading rule sets, and boundary-checked result entry | Grade auto-computed from `grading_rules`, Unique `(exam_id, student_id)` |
| **`fees`** | Fee invoices and ledger payment tracking | Invoices and payments stored in paise, dynamic balance computation |
| **`guardian`** | Guardian portal orchestration | Strict ownership enforcement (`guardian_id == current_user.id`) |
| **`reports`** | High-level metrics and financial summaries | Live dashboard aggregation, attendance and fee summaries |
| **`audit`** | Central transactional audit trail | Synchronous in-transaction logging with `JSONB` diffs |

---

## 3. Database Architecture & Neon.tech Branching

The system is configured to connect to PostgreSQL on **Neon.tech**:

- **Pooled Connection (`DATABASE_URL`, Port 6543)**:
  - Connects to Neon's PgBouncer connection pooler.
  - Used by the FastAPI application runtime via `create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)`.
  - Enables hundreds of concurrent web requests to run efficiently without exhausting Postgres connection limits.
  - `pool_pre_ping=True` handles serverless compute auto-suspend transparently.

- **Direct Connection (`DATABASE_URL_DIRECT`, Port 5432)**:
  - Connects directly to the PostgreSQL compute instance, bypassing PgBouncer.
  - Used exclusively by **Alembic migrations** because transactional DDL, schema locks, and migration statements require session-level direct connections.

---

## 4. Standard Response Contracts

Every endpoint guarantees one of three standard response structures:

### Success Response:
```json
{
  "success": true,
  "data": {},
  "message": "Done"
}
```

### Error Response:
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_ATTENDANCE",
    "message": "Attendance already recorded for this student on this date and session"
  }
}
```

### Paginated List Response:
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 143,
    "pages": 8
  }
}
```

