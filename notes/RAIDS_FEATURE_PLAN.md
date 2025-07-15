# Raids Feature Implementation Plan

## 1. Database Model
- **File:** `app/models/raid.py`
- **Fields:**
  - `id` (PK, integer, autoincrement)
  - `datetime` (datetime, required) — when the raid is scheduled
  - `scenario_id` (FK to Scenarios, required) — which raid instance
  - `difficulty` (string, required) — e.g., "Normal", "Heroic", "Mythic"
  - `size` (integer, required) — number of players
  - `created_at` (datetime, default now)
  - `updated_at` (datetime, auto-update)
  - `team_id` (FK to Teams, required) — which team is running the raid
- **Relationships:**
  - Many-to-one: Each Raid belongs to a Team (`team_id`)
  - Many-to-one: Each Raid references a Scenario (`scenario_id`)
  - One-to-many: Raid has many Attendance records
- **Constraints:**
  - `difficulty` should be an enum or validated string (Normal, Heroic, Mythic, etc.)
  - `size` should be a positive integer
- **Tests:**
  - Model creation, constraints, relationships, and edge cases

---

## 2. Pydantic Schemas
- **File:** `app/schemas/raid.py`
- **Schemas:**
  - `RaidBase`: Common fields (`datetime`, `scenario_id`, `difficulty`, `size`, `team_id`)
  - `RaidCreate`: Inherits from `RaidBase`
  - `RaidUpdate`: Optional fields for PATCH/PUT
  - `RaidResponse`: All fields, including `id`, `created_at`, `updated_at`
- **Validation:**
  - `difficulty` must be one of the allowed values
  - `size` must be positive
  - `datetime` must be a valid datetime
- **Tests:**
  - Schema validation, serialization, and edge cases

---

## 3. API Router
- **File:** `app/routers/raid.py`
- **Endpoints:**
  - `POST /raids/` - Create new raid (superuser only)
  - `GET /raids/` - List all raids (any valid token)
  - `GET /raids/{raid_id}` - Get raid by ID (any valid token)
  - `GET /raids/team/{team_id}` - List all raids for a team (any valid token)
  - `PUT /raids/{raid_id}` - Update raid (superuser only)
  - `DELETE /raids/{raid_id}` - Delete raid (superuser only)
- **Behaviors:**
  - Enforce valid scenario and team references
  - Proper permissions (superuser for create/update/delete)
  - Return appropriate error messages for constraint violations
- **Tests:**
  - CRUD, permissions, filtering, error cases

---

## 4. Feature Tests
- **File:** `tests/feature/test_raid_router.py`
- **Coverage:**
  - All endpoints
  - Permissions (superuser vs regular user)
  - Filtering by team
  - Validation and error handling

---

## 5. Integration
- **main.py:** Add Raid router to FastAPI app
- **README:** Document Raid endpoints and behaviors

---

## 6. Future/Optional
- **Attendance Integration:** Ensure Attendance records reference raids correctly
- **Cascade Deletes:** Deleting a team or scenario deletes associated raids (test this)
- **Admin UI:** (If applicable) Add Raid management to frontend

---

## Summary Table

| Phase         | File(s)                        | Key Tasks/Notes                                 |
|---------------|-------------------------------|-------------------------------------------------|
| Model         | models/raid.py                 | Fields, relationships, constraints, tests       |
| Schemas       | schemas/raid.py                | Pydantic models, validation, tests              |
| API Router    | routers/raid.py                | CRUD, permissions, logic, tests                 |
| Feature Tests | tests/feature/test_raid_router.py | All endpoint and edge case tests                |
| Integration   | main.py, README.md             | Add router, document endpoints                  |
