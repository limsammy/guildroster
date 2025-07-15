# Attendance Feature Implementation Plan

## Overview
The Attendance feature will track which toons (characters) attended specific raids, enabling guilds to monitor participation, track attendance patterns, and generate attendance reports. This is a critical feature for guild management and raid organization.

## Current State Analysis

### Existing Infrastructure
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **API**: FastAPI with automatic documentation
- **Authentication**: Token-based system with superuser and regular user roles
- **Testing**: Comprehensive pytest suite with feature tests
- **Models**: Raid, Toon, Member, Team, Scenario models already implemented
- **Relationships**: Raid ↔ Toon relationship is planned but not implemented

### Schema Design (from diagram)
The Attendance table should have:
- `id` - Primary key
- `raid_id` - Foreign key to Raids
- `toon_id` - Foreign key to Toons  
- `is_present` - Boolean indicating attendance
- `created_at` - Timestamp
- `updated_at` - Timestamp

## Implementation Phases

### Phase 1: Database Model (`app/models/attendance.py`)

**Objective**: Create the Attendance model with proper relationships and constraints

**Fields**:
- `id` - Primary key (Integer, auto-increment)
- `raid_id` - Foreign key to raids table (Integer, not null)
- `toon_id` - Foreign key to toons table (Integer, not null)
- `is_present` - Boolean indicating attendance (Boolean, not null, default True)
- `notes` - Optional attendance notes (String(500), nullable)
- `created_at` - Timestamp (DateTime, default now)
- `updated_at` - Timestamp (DateTime, default now, onupdate now)

**Relationships**:
- **Raid** - Many-to-one relationship (many attendance records per raid)
- **Toon** - Many-to-one relationship (many attendance records per toon)

**Constraints**:
- Unique constraint on `(raid_id, toon_id)` to prevent duplicate attendance records
- Foreign key constraints with cascade delete
- Check constraint ensuring notes are not empty strings

**Updates to Existing Models**:
- Uncomment and implement attendance relationship in Raid model
- Add attendance relationship to Toon model

**Deliverables**:
- `app/models/attendance.py` - Attendance model
- Updates to `app/models/raid.py` - Add attendance relationship
- Updates to `app/models/toon.py` - Add attendance relationship
- Updates to `app/models/__init__.py` - Import attendance model

### Phase 2: Pydantic Schemas (`app/schemas/attendance.py`)

**Objective**: Create comprehensive schemas for API requests and responses

**Schemas**:
- `AttendanceBase` - Core fields with validation
- `AttendanceCreate` - For creating new attendance records
- `AttendanceUpdate` - For partial updates
- `AttendanceResponse` - For API responses with nested raid and toon data
- `AttendanceBulkCreate` - For bulk attendance operations
- `AttendanceBulkUpdate` - For bulk attendance updates

**Validation**:
- Raid and toon existence validation
- Duplicate attendance prevention
- Notes length validation (max 500 characters)
- Boolean validation for is_present

**Deliverables**:
- `app/schemas/attendance.py` - All attendance schemas
- Updates to `app/schemas/__init__.py` - Import attendance schemas

### Phase 3: API Router (`app/routers/attendance.py`)

**Objective**: Implement comprehensive API endpoints for attendance management

**Endpoints**:
- `POST /attendance/` - Create single attendance record (superuser only)
- `POST /attendance/bulk` - Create multiple attendance records (superuser only)
- `GET /attendance/` - List attendance records with filtering (any valid token)
- `GET /attendance/{attendance_id}` - Get attendance by ID (any valid token)
- `GET /attendance/raid/{raid_id}` - Get all attendance for a raid (any valid token)
- `GET /attendance/toon/{toon_id}` - Get all attendance for a toon (any valid token)
- `GET /attendance/member/{member_id}` - Get all attendance for a member's toons (any valid token)
- `GET /attendance/team/{team_id}` - Get all attendance for a team's raids (any valid token)
- `PUT /attendance/{attendance_id}` - Update attendance record (superuser only)
- `PUT /attendance/bulk` - Update multiple attendance records (superuser only)
- `DELETE /attendance/{attendance_id}` - Delete attendance record (superuser only)

**Features**:
- Comprehensive filtering (by raid, toon, member, team, date range)
- Bulk operations for efficient data entry
- Proper authentication and authorization
- Validation of raid and toon relationships

**Deliverables**:
- `app/routers/attendance.py` - Attendance router with all endpoints
- Updates to `app/main.py` - Include attendance router

### Phase 4: Feature Tests (`tests/feature/test_attendance_router.py`)

**Objective**: Comprehensive test coverage for all attendance functionality

**Test Categories**:
- **CRUD Operations**: Create, read, update, delete attendance records
- **Bulk Operations**: Bulk create and update functionality
- **Authentication**: Superuser vs regular user permissions
- **Validation**: Data validation and constraint testing
- **Filtering**: All filter endpoints and query parameters
- **Relationships**: Raid and toon relationship integrity
- **Error Handling**: Invalid data, missing records, constraint violations
- **Edge Cases**: Duplicate records, cascade deletes, etc.

**Test Structure**:
- Follow existing test patterns from other routers
- Include helper methods for creating test data
- Test both positive and negative scenarios
- Verify database constraints and relationships

**Deliverables**:
- `tests/feature/test_attendance_router.py` - Comprehensive feature tests
- `tests/model/test_attendance.py` - Model-specific tests
- `tests/schema/test_attendance.py` - Schema validation tests

### Phase 5: Database Migration

**Objective**: Create and apply database migration for attendance table

**Migration Steps**:
1. Generate migration using Alembic
2. Create attendance table with all constraints
3. Add indexes for performance
4. Test migration rollback

**Migration SQL**:
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    raid_id INTEGER NOT NULL REFERENCES raids(id) ON DELETE CASCADE,
    toon_id INTEGER NOT NULL REFERENCES toons(id) ON DELETE CASCADE,
    is_present BOOLEAN NOT NULL DEFAULT TRUE,
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(raid_id, toon_id),
    CHECK(notes IS NULL OR TRIM(notes) != '')
);

CREATE INDEX idx_attendance_raid_id ON attendance(raid_id);
CREATE INDEX idx_attendance_toon_id ON attendance(toon_id);
CREATE INDEX idx_attendance_created_at ON attendance(created_at);
```

**Deliverables**:
- Alembic migration file for attendance table
- Database indexes for performance optimization

### Phase 6: Enhanced Reporting Features

**Objective**: Add attendance reporting and analytics endpoints

**Additional Endpoints**:
- `GET /attendance/stats/raid/{raid_id}` - Attendance statistics for a raid
- `GET /attendance/stats/toon/{toon_id}` - Attendance statistics for a toon
- `GET /attendance/stats/member/{member_id}` - Attendance statistics for a member
- `GET /attendance/stats/team/{team_id}` - Attendance statistics for a team
- `GET /attendance/report/date-range` - Attendance report for date range

**Statistics Include**:
- Total raids attended/missed
- Attendance percentage
- Streak information (consecutive attendance)
- Role-based attendance breakdown
- Time-based attendance patterns

**Deliverables**:
- Enhanced attendance router with reporting endpoints
- Statistics calculation utilities
- Updated feature tests for reporting endpoints

### Phase 7: Documentation Updates

**Objective**: Update project documentation to include attendance feature

**Updates Required**:
- **README.md**: Add attendance to features list and API endpoints
- **API Documentation**: Update OpenAPI schema with new endpoints
- **Database Schema**: Update schema documentation
- **Examples**: Add attendance usage examples

**Deliverables**:
- Updated README.md with attendance documentation
- API documentation examples
- Database schema documentation updates

## Implementation Order

1. **Phase 1**: Create Attendance model with relationships
2. **Phase 2**: Implement Pydantic schemas
3. **Phase 3**: Build API router with core endpoints
4. **Phase 4**: Write comprehensive feature tests
5. **Phase 5**: Create and apply database migration
6. **Phase 6**: Add reporting and analytics features
7. **Phase 7**: Update documentation

## Technical Considerations

### Performance Optimizations
- **Indexes**: Add indexes on frequently queried fields (raid_id, toon_id, created_at)
- **Bulk Operations**: Support bulk create/update for efficient data entry
- **Query Optimization**: Use proper joins and eager loading for related data
- **Pagination**: Implement pagination for large attendance datasets

### Data Integrity
- **Unique Constraints**: Prevent duplicate attendance records
- **Foreign Key Constraints**: Ensure referential integrity
- **Cascade Deletes**: Handle cleanup when raids or toons are deleted
- **Validation**: Comprehensive input validation and error handling

### User Experience
- **Bulk Operations**: Allow efficient entry of attendance data
- **Flexible Filtering**: Multiple ways to query attendance data
- **Clear Error Messages**: Helpful error messages for validation failures
- **Comprehensive Reporting**: Rich statistics and analytics

## Example Data Structure

```json
{
  "raid_id": 1,
  "toon_id": 5,
  "is_present": true,
  "notes": "On time, performed well"
}
```

## Bulk Operations Example

```json
{
  "attendance_records": [
    {
      "raid_id": 1,
      "toon_id": 5,
      "is_present": true,
      "notes": "On time"
    },
    {
      "raid_id": 1,
      "toon_id": 7,
      "is_present": false,
      "notes": "No show"
    }
  ]
}
```

## Future Enhancements

### Phase 8: Advanced Features (Future)
- **Attendance Templates**: Pre-configured attendance lists for common raid compositions
- **Auto-attendance**: Automatic attendance marking based on raid completion
- **Attendance Notifications**: Alerts for missing attendance records
- **Attendance Import/Export**: CSV import/export functionality
- **Attendance Analytics**: Advanced analytics and trend analysis
- **Mobile Support**: Optimized endpoints for mobile applications

### Integration Opportunities
- **Raid Completion Tracking**: Link attendance to actual raid completion
- **Loot Distribution**: Track attendance for loot distribution calculations
- **Performance Metrics**: Correlate attendance with raid performance
- **Guild Progression**: Use attendance data for guild progression tracking

## Testing Strategy

### Model Tests (`tests/model/test_attendance.py`)
- Attendance creation with valid data
- Constraint validation (unique constraints, foreign keys)
- Relationship testing with raids and toons
- Cascade delete behavior

### Schema Tests (`tests/schema/test_attendance.py`)
- Field validation
- Serialization/deserialization
- Bulk operation validation
- Error handling

### Feature Tests (`tests/feature/test_attendance_router.py`)
- All CRUD operations
- Bulk operations
- Authentication and authorization
- Filtering and search
- Error handling
- Integration with raid and toon systems

## Migration Strategy

### Step 1: Create Attendance Table
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    raid_id INTEGER NOT NULL REFERENCES raids(id) ON DELETE CASCADE,
    toon_id INTEGER NOT NULL REFERENCES toons(id) ON DELETE CASCADE,
    is_present BOOLEAN NOT NULL DEFAULT TRUE,
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(raid_id, toon_id),
    CHECK(notes IS NULL OR TRIM(notes) != '')
);
```

### Step 2: Add Performance Indexes
```sql
CREATE INDEX idx_attendance_raid_id ON attendance(raid_id);
CREATE INDEX idx_attendance_toon_id ON attendance(toon_id);
CREATE INDEX idx_attendance_created_at ON attendance(created_at);
```

### Step 3: Update Existing Models
- Add attendance relationships to Raid and Toon models
- Update model imports and exports

This comprehensive plan provides a structured approach to implementing the Attendance feature while maintaining consistency with the existing codebase patterns and preparing for future enhancements. 