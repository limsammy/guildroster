I'll review the README and schema diagram to understand the Guilds implementation requirements and create a plan.

Read file: README.md
Ran tool
Ran tool
Read file: app/models/__init__.py
Ran tool
Ran tool
Read file: app/main.py
Based on my review of the README, schema diagram, and current codebase structure, here's my plan for implementing Guilds:

## Guilds Implementation Plan

### 📋 Overview
Guilds are the core organizational unit in GuildRoster, representing World of Warcraft guilds that contain teams, members, and characters. This implementation will provide full CRUD operations for guild management with proper authentication and authorization.

### 🏗️ Architecture Components

#### **1. Database Model** (`app/models/guild.py`)
```python
class Guild(Base):
    id: Primary key
    name: Guild name (unique)
    description: Guild description
    realm: WoW realm/server
    faction: Alliance/Horde
    website: Optional guild website
    discord: Optional Discord server
    is_active: Active status
    created_at: Creation timestamp
    updated_at: Last update timestamp
    created_by: User who created the guild (FK to Users)
```

#### **2. Pydantic Schemas** (`app/schemas/guild.py`)
- `GuildCreate` - For creating new guilds
- `GuildUpdate` - For updating existing guilds  
- `GuildResponse` - For API responses
- `GuildList` - For paginated guild listings

#### **3. API Endpoints** (`app/routers/guild.py`)
- `POST /guilds/` - Create new guild (superuser only)
- `GET /guilds/` - List guilds (paginated, any valid token)
- `GET /guilds/{id}` - Get guild by ID (any valid token)
- `GET /guilds/name/{name}` - Get guild by name (any valid token)
- `PUT /guilds/{id}` - Update guild (superuser only)
- `DELETE /guilds/{id}` - Delete guild (superuser only)
- `POST /guilds/{id}/activate` - Activate guild (superuser only)
- `POST /guilds/{id}/deactivate` - Deactivate guild (superuser only)

#### **4. Authentication & Authorization**
- **Create/Update/Delete**: Superuser only
- **Read operations**: Any valid token
- **Guild ownership**: Track who created each guild

#### **5. Validation Rules**
- Guild name: Required, unique, 3-50 characters
- Realm: Required, valid WoW realm format
- Faction: Required, must be "Alliance" or "Horde"
- Description: Optional, max 500 characters
- Website/Discord: Optional, valid URL format

### �� Testing Strategy

#### **Unit Tests** (`tests/unit/test_guild_model.py`)
- Guild model creation and validation
- Field constraints and relationships
- Database operations

#### **Integration Tests** (`tests/feature/test_guild_api.py`)
- API endpoint functionality
- Authentication and authorization
- CRUD operations
- Error handling
- Pagination

#### **Test Scenarios**
- Create guild with valid data
- Create guild with duplicate name (should fail)
- Update guild information
- Delete guild
- Activate/deactivate guild
- List guilds with pagination
- Access control (superuser vs regular user)

### 📁 File Structure
```
app/
├── models/
│   └── guild.py          # Guild database model
├── schemas/
│   └── guild.py          # Guild Pydantic schemas
├── routers/
│   └── guild.py          # Guild API endpoints
└── __init__.py           # Update imports

tests/
├── unit/
│   └── test_guild_model.py    # Guild model tests
└── feature/
    └── test_guild_api.py      # Guild API tests
```

### 🔄 Implementation Order

1. **Database Model** - Create Guild model with proper relationships
2. **Pydantic Schemas** - Define request/response schemas
3. **API Router** - Implement CRUD endpoints with auth
4. **Update Main App** - Include guild router
5. **Unit Tests** - Test model and schema validation
6. **Integration Tests** - Test API endpoints
7. **Documentation** - Update README with guild examples

### �� Key Features

- **Full CRUD Operations**: Create, read, update, delete guilds
- **Authentication**: Token-based access control
- **Authorization**: Superuser-only for modifications
- **Validation**: Comprehensive input validation
- **Pagination**: Efficient guild listing
- **Audit Trail**: Track creation and updates
- **Status Management**: Activate/deactivate guilds

### �� Future Integration Points

- **Teams**: Guilds will contain multiple teams
- **Members**: Guild members will be associated with guilds
- **Characters**: Characters will belong to guild members
- **Raids**: Raids will be organized within guilds

This implementation provides a solid foundation for the guild management system while maintaining consistency with the existing authentication and API patterns in the codebase.