Here’s a phased plan for removing the Member model and table, so only Toons remain:

---

## **Phase 1: Preparation & Analysis**
- Audit all backend and frontend code for references to Member (models, schemas, endpoints, UI, state, tests, docs).
- Identify all relationships and dependencies between Member and other entities (especially Toon).
- Plan data migration if any Member data needs to be preserved or moved to Toon.

---

## **Phase 2: Backend Refactor**

### 2.1. Models & Database
- Remove the Member model.
- Update Toon and other models to remove references to Member.
- Update or remove any foreign keys or relationships in the database.
- Write and test a migration script to drop the member table and migrate any necessary data.

### 2.2. Schemas & Business Logic
- Remove Member schemas.
- Update Toon schemas and business logic to be independent of Member.
- Refactor or remove utility functions that reference Member.

### 2.3. Routers/Endpoints
- Remove all member-related API endpoints.
- Update other endpoints (e.g., toon, team, guild) to not require or return member data.

### 2.4. Backend Tests
- Remove or update tests that reference Member.
- Add/adjust tests for toon-only logic.

---

## **Phase 3: Frontend Refactor**

### 3.1. API Types & Calls
- Remove Member types and interfaces.
- Delete or update API calls that reference members.
- Update toon-related API calls.

### 3.2. UI Components & Pages
- Remove member-related components (forms, lists, etc.).
- Update toon-related components to not reference members.
- Remove member-related routes/pages and update navigation.

### 3.3. State Management
- Remove member-related state from global stores.
- Update toon state as needed.

### 3.4. Frontend Tests
- Remove or update tests that reference members.
- Add/adjust tests for toon-only flows.

---

## **Phase 4: Documentation & Cleanup**
- Update documentation (README, API docs, diagrams) to remove references to members.
- Clean up any remaining references in comments, TODOs, or code.
- Communicate breaking changes to stakeholders.

---

## **Phase 5: Final Migration & Deployment**
- Run migration scripts on staging, then production.
- Deploy backend and frontend changes.
- Monitor for issues and verify toon-only flows work as expected.

---

Would you like a todo checklist for these phases, or to start with a specific phase?