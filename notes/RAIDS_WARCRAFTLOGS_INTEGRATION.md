# **WarcraftLogs JSON Storage Implementation Plan**

## **Phase 1: Database Schema Updates**

### **Step 1.1: Update Raid Model**
- **File**: `app/models/raid.py`
- **Changes**:
  - Add `warcraftlogs_report_code` (String(50), nullable=True, indexed)
  - Add `warcraftlogs_metadata` (JSON, nullable=True)
  - Add `warcraftlogs_participants` (JSON, nullable=True)
  - Add `warcraftlogs_fights` (JSON, nullable=True)
  - Add `warcraftlogs_fetched_at` (DateTime, nullable=True)

### **Step 1.2: Create Database Migration**
- **File**: `migrations/versions/xxx_add_warcraftlogs_json_fields.py`
- **SQL**:
  ```sql
  ALTER TABLE raids 
  ADD COLUMN warcraftlogs_report_code VARCHAR(50),
  ADD COLUMN warcraftlogs_metadata JSONB,
  ADD COLUMN warcraftlogs_participants JSONB,
  ADD COLUMN warcraftlogs_fights JSONB,
  ADD COLUMN warcraftlogs_fetched_at TIMESTAMP;
  
  CREATE INDEX idx_raids_warcraftlogs_report_code ON raids(warcraftlogs_report_code);
  ```

### **Step 1.3: Update Pydantic Schemas**
- **File**: `app/schemas/raid.py`
- **Changes**:
  - Add JSON fields to `RaidCreate` and `RaidResponse` schemas
  - Add validation for WarcraftLogs URL format
  - Add optional fields for stored JSON data

---

## **Phase 2: Core Data Processing Logic**

### **Step 2.1: Create WarcraftLogs Processing Utility**
- **File**: `app/utils/warcraftlogs_processor.py`
- **Functions**:
  - `process_warcraftlogs_report(raid_id: int, warcraftlogs_url: str)`
  - `auto_populate_attendance_from_stored_data(raid_id: int)`
  - `extract_and_validate_report_code(url: str)`

### **Step 2.2: Update Raid Router**
- **File**: `app/routers/raid.py`
- **Changes**:
  - Modify `create_raid` to process WarcraftLogs URL if provided
  - Add error handling for WarcraftLogs API failures
  - Ensure raid creation succeeds even if WarcraftLogs fails

### **Step 2.3: Add WarcraftLogs Data Endpoints**
- **File**: `app/routers/raid.py`
- **New Endpoints**:
  - `GET /raids/{raid_id}/warcraftlogs` - Get stored data
  - `POST /raids/{raid_id}/auto-attendance` - Auto-populate attendance

---

## **Phase 3: Attendance Integration**

### **Step 3.1: Update Attendance Router**
- **File**: `app/routers/attendance.py`
- **Changes**:
  - Add bulk creation endpoint for WarcraftLogs participants
  - Add validation to prevent duplicate attendance records
  - Add logging for auto-population actions

### **Step 3.2: Create Attendance Auto-Population Logic**
- **File**: `app/utils/attendance_processor.py`
- **Functions**:
  - `match_participants_to_toons(participants: List[Dict])`
  - `create_attendance_records(raid_id: int, participants: List[Dict])`
  - `validate_attendance_creation(raid_id: int, toon_id: int)`

---

## **Phase 4: Error Handling & Validation**

### **Step 4.1: Add Comprehensive Error Handling**
- **Files**: All router files
- **Error Types**:
  - Invalid WarcraftLogs URL format
  - API rate limiting
  - Network timeouts
  - Invalid report codes
  - Participant matching failures

### **Step 4.2: Add Data Validation**
- **File**: `app/utils/validators.py`
- **Validations**:
  - WarcraftLogs URL format validation
  - JSON data structure validation
  - Participant data completeness
  - Class name mapping validation

---

## **Phase 5: Testing & Documentation**

### **Step 5.1: Update Model Tests**
- **File**: `tests/model/test_raid_model.py`
- **Tests**:
  - JSON field storage and retrieval
  - Report code indexing
  - Data integrity constraints

### **Step 5.2: Add Integration Tests**
- **File**: `tests/feature/test_warcraftlogs_integration.py`
- **Tests**:
  - End-to-end WarcraftLogs processing
  - Attendance auto-population
  - Error handling scenarios
  - Data validation

### **Step 5.3: Update API Documentation**
- **File**: `README.md`
- **Updates**:
  - Add WarcraftLogs integration documentation
  - Update API endpoint documentation
  - Add usage examples

---

## **Phase 6: Frontend Integration**

### **Step 6.1: Update Frontend Types**
- **File**: `frontend/app/api/types.ts`
- **Changes**:
  - Add WarcraftLogs fields to Raid interface
  - Add new API endpoint types
  - Add participant and fight data types

### **Step 6.2: Update Raid Form**
- **File**: `frontend/app/components/ui/RaidForm.tsx`
- **Changes**:
  - Add WarcraftLogs URL validation
  - Add loading states for data processing
  - Add success/error feedback

### **Step 6.3: Add Attendance Auto-Population UI**
- **File**: `frontend/app/components/ui/AttendanceAutoPopulate.tsx`
- **Features**:
  - Button to trigger auto-population
  - Preview of participants to be added
  - Confirmation dialog
  - Progress indicators

---

## **Implementation Order:**

1. **Phase 1** - Database schema (foundation)
2. **Phase 2** - Core processing logic (backbone)
3. **Phase 3** - Attendance integration (main feature)
4. **Phase 4** - Error handling (reliability)
5. **Phase 5** - Testing & docs (quality)
6. **Phase 6** - Frontend (user experience)

---

## **Success Criteria:**

- ✅ WarcraftLogs data is fetched and stored once per raid
- ✅ Attendance records can be auto-populated from participant data
- ✅ All error scenarios are handled gracefully
- ✅ Comprehensive test coverage (90%+)
- ✅ Frontend provides intuitive user experience
- ✅ Documentation is complete and accurate

This plan provides a clear, step-by-step approach to implementing the WarcraftLogs JSON storage feature with proper separation of concerns and comprehensive testing.