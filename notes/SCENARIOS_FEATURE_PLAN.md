# Scenarios Feature Implementation Plan

## Overview
The Scenarios feature will provide raid instance lookup functionality, allowing guilds to reference specific World of Warcraft raid instances when scheduling raids. This will enable better tracking and organization of raid activities.

## Phase 1: Database Model (`app/models/scenario.py`)

### Fields (based on typical WoW raid instance structure):
- `id` - Primary key
- `name` - Raid instance name (e.g., "Blackrock Foundry", "Hellfire Citadel")
- `expansion` - WoW expansion (e.g., "Warlords of Draenor", "Legion")
- `min_level` - Minimum character level required
- `max_level` - Maximum character level (usually 60, 70, 80, etc.)
- `difficulty_support` - JSON array of supported difficulties (Normal, Heroic, etc.)
- `size_support` - JSON array of supported sizes (10, 25)
- `is_active` - Boolean for current/retired raids
- `created_at` - Timestamp
- `updated_at` - Timestamp

### Relationships:
- **Raids** - One-to-many relationship (one scenario can have many raids)
- **No direct guild/team relationships** - Scenarios are global lookup data

### Constraints:
- Unique constraint on `name` (raid names should be unique)
- Check constraints for valid expansions, levels, difficulties, sizes
- Non-empty name validation

## Phase 2: Pydantic Schemas (`app/schemas/scenario.py`)

### Schemas:
- `ScenarioBase` - Core fields with validation
- `ScenarioCreate` - For creating new scenarios
- `ScenarioUpdate` - For partial updates
- `ScenarioResponse` - For API responses

### Validation:
- Enum validation for expansions, difficulties, sizes
- Level range validation (min_level <= max_level)
- JSON array validation for difficulty_support and size_support

## Phase 3: API Router (`app/routers/scenario.py`)

### Endpoints:
- `POST /scenarios/` - Create new scenario (superuser only)
- `GET /scenarios/` - List all scenarios (any valid token)
- `GET /scenarios/{scenario_id}` - Get scenario by ID (any valid token)
- `GET /scenarios/expansion/{expansion}` - Get scenarios by expansion (any valid token)
- `PUT /scenarios/{scenario_id}` - Update scenario (superuser only)
- `DELETE /scenarios/{scenario_id}` - Delete scenario (superuser only)

### Features:
- Filtering by expansion
- Search by name (optional)
- Pagination support
- Proper authentication and authorization

## Phase 4: Feature Tests (`tests/feature/test_scenario_router.py`)

### Test Coverage:
- All CRUD operations
- Authentication requirements
- Validation testing
- Expansion filtering
- Error handling
- Data integrity

## Phase 5: Integration with Raids

### Update Raid Model:
- Uncomment and implement `scenario_id` field in Raid model
- Add relationship to Scenario
- Update Raid schemas to include scenario_id
- Update Raid router to validate scenario existence

### Update Raid Tests:
- Add scenario validation tests
- Test raid creation with scenarios
- Test scenario relationship integrity

## Phase 6: Documentation Updates

### README Updates:
- Add Scenarios to features list
- Document all scenario endpoints
- Update database schema section
- Add relationship documentation

## Implementation Order

1. **Phase 1**: Create Scenario model with proper constraints
2. **Phase 2**: Implement Pydantic schemas with validation
3. **Phase 3**: Build API router with all endpoints
4. **Phase 4**: Write comprehensive feature tests
5. **Phase 5**: Integrate with existing Raid functionality
6. **Phase 6**: Update documentation

## Database Migration

The implementation will require:
1. Create scenarios table
2. Add scenario_id to raids table (foreign key)
3. Update existing raid records (if any) to reference scenarios

## Example Data Structure

```json
{
  "name": "Blackrock Foundry",
  "expansion": "Warlords of Draenor",
  "min_level": 90,
  "max_level": 100,
  "difficulty_support": ["Normal", "Heroic"],
  "size_support": ["10", "25"],
  "is_active": true
}
```

## Technical Considerations

### WoW Expansions:
- Classic/Vanilla
- The Burning Crusade
- Wrath of the Lich King
- Cataclysm
- Mists of Pandaria
- Warlords of Draenor
- Legion
- Battle for Azeroth
- Shadowlands
- Dragonflight

### Difficulty Support:
- Normal
- Heroic
- Mythic
- Raid Finder (for applicable expansions)

### Size Support:
- 10-man
- 25-man
- Flexible (for applicable expansions)

## Future Enhancements

### Phase 7: Advanced Features (Future)
- Boss encounter tracking within scenarios
- Loot table integration
- Achievement tracking
- Historical raid completion data
- Scenario rotation schedules

### Integration Opportunities:
- Attendance tracking with specific encounters
- Loot distribution tracking
- Performance metrics per scenario
- Guild progression tracking

## Testing Strategy

### Model Tests:
- Scenario creation with valid data
- Constraint validation (unique names, valid expansions)
- Relationship testing with raids
- Cascade delete behavior

### Schema Tests:
- Field validation
- Enum validation
- JSON array validation
- Serialization/deserialization

### Feature Tests:
- All CRUD operations
- Authentication and authorization
- Error handling
- Filtering and search
- Integration with raid system

## Migration Strategy

### Step 1: Create Scenarios Table
```sql
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    expansion VARCHAR(50) NOT NULL,
    min_level INTEGER NOT NULL,
    max_level INTEGER NOT NULL,
    difficulty_support JSONB NOT NULL,
    size_support JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Step 2: Add Scenario Reference to Raids
```sql
ALTER TABLE raids ADD COLUMN scenario_id INTEGER REFERENCES scenarios(id);
```

### Step 3: Populate Initial Data
- Add common raid scenarios from various expansions
- Set up proper difficulty and size support arrays

This plan provides a comprehensive approach to implementing the Scenarios feature while maintaining consistency with the existing codebase patterns and preparing for future integration with the Raids system. 