Here’s a detailed plan for implementing the **Toon** feature in the GuildRoster project, based on the README and the provided schema diagram. This plan follows the same phased approach as the Members feature, ensuring consistency and test coverage.

---

## Toon Feature Implementation Plan

### 1. **Database Model**
- **File:** `app/models/toon.py`
- **Fields:**
  - `id` (PK, integer, autoincrement)
  - `username` (string, required, unique per member)
  - `is_main` (boolean, default False)
  - `created_at` (datetime, default now)
  - `updated_at` (datetime, auto-update)
  - `member_id` (FK to Members, required)
  - `class` (string, required)
  - `role` (string, required)
- **Relationships:**
  - Many-to-one: Each Toon belongs to a Member (`member_id`)
  - One-to-many: Member has many Toons
  - Attendance: Toons are referenced in Attendance records (FK)
- **Constraints:**
  - Unique constraint: (`member_id`, `username`) to prevent duplicate toon names for the same member
  - Only one toon per member can have `is_main=True` (enforced in code or via DB constraint)
- **Tests:**
  - Model creation, constraints, relationships, and edge cases

---

### 2. **Pydantic Schemas**
- **File:** `app/schemas/toon.py`
- **Schemas:**
  - `ToonBase`: Common fields (`username`, `is_main`)
  - `ToonCreate`: Inherits from `ToonBase`, requires `member_id`
  - `ToonUpdate`: Optional fields for PATCH/PUT
  - `ToonResponse`: All fields, including `id`, `created_at`, `updated_at`, `member_id`
- **Validation:**
  - Username required, non-empty
  - is_main is boolean
  - member_id required for create
- **Tests:**
  - Schema validation, serialization, and edge cases

---

### 3. **API Router**
- **File:** `app/routers/toon.py`
- **Endpoints:**
  - `POST /toons/` - Create new toon (superuser only)
  - `GET /toons/` - List all toons (any valid token)
  - `GET /toons/{toon_id}` - Get toon by ID (any valid token)
  - `GET /toons/member/{member_id}` - List all toons for a member (any valid token)
  - `PUT /toons/{toon_id}` - Update toon (superuser only)
  - `DELETE /toons/{toon_id}` - Delete toon (superuser only)
- **Behaviors:**
  - Enforce unique username per member
  - Enforce only one main toon per member
  - Proper permissions (superuser for create/update/delete)
  - Return appropriate error messages for constraint violations
- **Tests:**
  - CRUD, permissions, filtering, error cases

---

### 4. **Feature Tests**
- **File:** `tests/feature/test_toon_router.py`
- **Coverage:**
  - All endpoints
  - Permissions (superuser vs regular user)
  - Unique constraints
  - Main toon logic
  - Filtering by member
  - Error handling

---

### 5. **Integration**
- **main.py:** Add Toon router to FastAPI app
- **README:** Document Toon endpoints and behaviors

---

### 6. **Future/Optional**
- **Attendance Integration:** Ensure Attendance records reference toons correctly
- **Cascade Deletes:** Deleting a member deletes their toons (test this)
- **Admin UI:** (If applicable) Add Toon management to frontend

---

## Summary Table

| Phase         | File(s)                        | Key Tasks/Notes                                 |
|---------------|-------------------------------|-------------------------------------------------|
| Model         | models/toon.py                 | Fields, relationships, constraints, tests       |
| Schemas       | schemas/toon.py                | Pydantic models, validation, tests              |
| API Router    | routers/toon.py                | CRUD, permissions, logic, tests                 |
| Feature Tests | tests/feature/test_toon_router.py | All endpoint and edge case tests                |
| Integration   | main.py, README.md             | Add router, document endpoints                  |

---
