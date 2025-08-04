# Attendance Team View - Specifications & Implementation Plan

## Overview

Transform the current attendance page from a simple list view to a comprehensive team-based table view that shows toons as rows and raids as columns, with historical attendance data and percentage calculations.

## Current State Analysis

### Existing Infrastructure
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **API**: FastAPI with comprehensive attendance endpoints
- **Frontend**: React with TypeScript, existing attendance page with list view
- **Authentication**: Token-based system with superuser and regular user roles
- **Models**: Attendance, Raid, Toon, Team, Guild models with proper relationships

### Current Attendance Page Issues
- Simple list view doesn't provide historical context
- No team-based organization
- Difficult to see attendance patterns across multiple raids
- No percentage calculations
- Limited filtering options

## Feature Specifications

### 1. Team-Based Organization
- **Guild Dropdown**: Only visible to superusers, allows switching between guilds
- **Team Dropdown**: Shows teams for the selected guild, with "All Teams" option
- **Context Awareness**: Regular users only see teams from their current guild

### 2. Table View Structure
- **Rows**: Toons (characters) from the selected team(s)
- **Columns**: 
  - Toon Name (fixed)
  - Overall Attendance % (fixed)
  - Last N raids (configurable: 5, 10, 15, 20)
- **Attendance Status Indicators**:
  - ✅ Present (Green)
  - ❌ Absent (Red)
  - 🟡 Benched (Yellow)
  - * = Has note (displayed on hover)

### 3. Attendance Percentage Calculation
- **Formula**: `Present / (Total Raids - Benched)`
- **Exclusion**: Benched status does not count as absent
- **Display**: Percentage with color coding (green for high, yellow for medium, red for low)

### 4. Historical Data Management
- **Default View**: Last 5 raids
- **Pagination**: Increment by 5 (5, 10, 15, 20 raids)
- **Lazy Loading**: Load additional raid data as needed
- **Sorting**: Raids sorted by date (newest first)

### 5. Interactive Features
- **Tooltips**: Show attendance notes on hover
- **Star Indicator**: (*) for benched status with notes
- **Responsive Design**: Mobile-friendly card view
- **Horizontal Scrolling**: For many raid columns

## Technical Implementation Plan

### Phase 1: Backend API Enhancements

#### 1.1 New Team View Endpoint
**Endpoint**: `GET /attendance/team-view/{team_id}`
**Purpose**: Return toons with their attendance data for the last N raids

**Request Parameters**:
- `team_id` (path): Team ID to view
- `raid_count` (query): Number of raids to include (default: 5)
- `guild_id` (query): Guild ID for superuser filtering (optional)

**Response Structure**:
```json
{
  "team": {
    "id": 1,
    "name": "Team Alpha",
    "guild_id": 1
  },
  "toons": [
    {
      "id": 1,
      "username": "Player1",
      "class": "Warrior",
      "role": "Tank",
      "overall_attendance_percentage": 85.0,
      "attendance_records": [
        {
          "raid_id": 5,
          "raid_date": "2024-01-15T20:00:00Z",
          "status": "present",
          "notes": "On time",
          "has_note": true
        }
      ]
    }
  ],
  "raids": [
    {
      "id": 5,
      "scheduled_at": "2024-01-15T20:00:00Z",
      "scenario_name": "Mythic Amirdrassil"
    }
  ]
}
```

#### 1.2 Enhanced Stats Calculation
**Update**: `GET /attendance/stats/toon/{toon_id}`
**Changes**: Modify percentage calculation to exclude benched from denominator

**New Calculation**:
```python
# Old: attendance_percentage = present / total_raids
# New: attendance_percentage = present / (total_raids - benched)
```

#### 1.3 Guild Context Support
**New Endpoint**: `GET /guilds/{guild_id}/teams`
**Purpose**: Get teams for a specific guild (superuser only)

### Phase 2: Frontend Component Development

#### 2.1 New Attendance Team View Component
**File**: `frontend/app/components/AttendanceTeamView.tsx`
**Features**:
- Team-based table layout
- Guild/team dropdowns
- Raid pagination controls
- Responsive design
- Tooltip system

#### 2.2 Enhanced Filtering Controls
**Components**:
- `GuildDropdown.tsx` (superuser only)
- `TeamDropdown.tsx`
- `RaidCountSelector.tsx`

#### 2.3 Attendance Table Component
**File**: `frontend/app/components/AttendanceTable.tsx`
**Features**:
- Dynamic column generation
- Status indicators with tooltips
- Percentage display with color coding
- Horizontal scrolling support

### Phase 3: Data Management & Performance

#### 3.1 Lazy Loading Strategy
- **Initial Load**: Last 5 raids for selected team
- **Progressive Loading**: Load additional raids on demand
- **Caching**: Cache loaded data to prevent redundant API calls

#### 3.2 State Management
- **Team Selection**: Track selected team/guild
- **Raid Count**: Track number of raids to display
- **Loading States**: Handle loading states for different data fetching operations

## Database Schema Considerations

### Existing Schema Review
The current attendance schema supports all required features:
- `AttendanceStatus` enum (present, absent, benched)
- `notes` and `benched_note` fields for tooltip content
- Proper relationships with Raid, Toon, and Team models

### No Schema Changes Required
The existing database structure can support all planned features without modifications.

## API Endpoints to Create/Modify

### New Endpoints
1. `GET /attendance/team-view/{team_id}` - Team view with attendance data
2. `GET /guilds/{guild_id}/teams` - Get teams for guild (superuser)

### Modified Endpoints
1. `GET /attendance/stats/toon/{toon_id}` - Update percentage calculation
2. `GET /attendance/stats/team/{team_id}` - Update percentage calculation

## Frontend File Structure

```
frontend/app/
├── components/
│   ├── AttendanceTeamView.tsx      # Main team view component
│   ├── AttendanceTable.tsx         # Table component
│   ├── GuildDropdown.tsx           # Guild selection (superuser)
│   ├── TeamDropdown.tsx            # Team selection
│   └── RaidCountSelector.tsx       # Raid count pagination
├── routes/
│   └── attendance.tsx              # Updated main attendance page
└── api/
    └── attendance.ts               # Updated API service
```

## Implementation Phases

### Phase 1: Backend Foundation (Week 1)
- [ ] Create new team view endpoint
- [ ] Update attendance stats calculation
- [ ] Add guild teams endpoint
- [ ] Write tests for new endpoints

### Phase 2: Frontend Components (Week 2)
- [ ] Create AttendanceTeamView component
- [ ] Create AttendanceTable component
- [ ] Create dropdown components
- [ ] Implement tooltip system

### Phase 3: Integration & Polish (Week 3)
- [ ] Integrate components into main attendance page
- [ ] Implement lazy loading
- [ ] Add responsive design
- [ ] Performance optimization

### Phase 4: Testing & Documentation (Week 4)
- [ ] Write frontend tests
- [ ] Integration testing
- [ ] Update documentation
- [ ] User acceptance testing

## Success Criteria

### Functional Requirements
- [ ] Users can view attendance by team
- [ ] Superusers can switch between guilds
- [ ] Attendance percentages exclude benched status
- [ ] Tooltips show attendance notes
- [ ] Responsive design works on mobile
- [ ] Lazy loading works for large datasets

### Performance Requirements
- [ ] Initial page load < 2 seconds
- [ ] Additional raid loading < 1 second
- [ ] Smooth scrolling on desktop
- [ ] Mobile performance acceptable

### User Experience Requirements
- [ ] Intuitive team/guild selection
- [ ] Clear attendance status indicators
- [ ] Easy navigation between different raid counts
- [ ] Helpful tooltips with relevant information

## Risk Assessment

### Technical Risks
1. **Performance**: Large datasets could slow down the table
   - **Mitigation**: Implement lazy loading and pagination
2. **Mobile Experience**: Complex table might not work well on mobile
   - **Mitigation**: Responsive design with card view fallback

### User Experience Risks
1. **Information Overload**: Too many columns could overwhelm users
   - **Mitigation**: Default to 5 raids, allow expansion
2. **Complex Navigation**: Multiple dropdowns might confuse users
   - **Mitigation**: Clear labeling and contextual help

## Future Enhancements

### Phase 2 Features (Future)
- **Export Functionality**: Export attendance data to CSV/Excel
- **Advanced Filtering**: Filter by date ranges, scenarios, etc.
- **Attendance Trends**: Visual charts showing attendance patterns
- **Bulk Operations**: Edit multiple attendance records at once
- **Notifications**: Alerts for low attendance rates

### Integration Opportunities
- **Raid Scheduling**: Link to raid creation/editing
- **Character Management**: Quick access to character profiles
- **Team Management**: Integration with team roster management
- **Reporting**: Generate attendance reports for guild leadership

## Conclusion

This attendance team view feature will significantly improve the user experience by providing a comprehensive, team-based view of attendance data. The implementation plan balances functionality with performance, ensuring the feature works well for both small and large guilds.

The phased approach allows for iterative development and testing, reducing risk and ensuring quality delivery. The modular component design will make future enhancements easier to implement. 