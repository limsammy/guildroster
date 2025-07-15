# Members Implementation Plan

## Overview
Members represent guild members who can have multiple characters (toons) and participate in raids. This is a crucial component that bridges Users, Guilds, Teams, and the planned Toons system.

## Phase 1: Database Models

### Member Model (`app/models/member.py`)
```python
class Member(Base):
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)  # Optional team assignment
    
    # Member profile fields
    display_name = Column(String(50), nullable=False)
    rank = Column(String(20), default="Member")  # Guild rank
    join_date = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    guild = relationship("Guild", back_populates="members")
    team = relationship("Team", back_populates="members")
    toons = relationship("Toon", back_populates="member", cascade="all, delete-orphan")
```

### Update Existing Models
- **User Model**: Add `memberships` relationship
- **Guild Model**: Add `members` relationship  
- **Team Model**: Add `members` relationship

## Phase 2: Pydantic Schemas

### Member Schemas (`app/schemas/member.py`)
```python
class MemberBase(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)
    rank: str = Field(default="Member", max_length=20)
    team_id: Optional[int] = None

class MemberCreate(MemberBase):
    user_id: int
    guild_id: int

class MemberUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    rank: Optional[str] = Field(None, max_length=20)
    team_id: Optional[int] = None
    is_active: Optional[bool] = None

class MemberResponse(MemberBase):
    id: int
    user_id: int
    guild_id: int
    join_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

## Phase 3: API Router

### Member Router (`app/routers/member.py`)
**Endpoints:**
- `POST /members/` - Add member to guild (superuser only)
- `GET /members/` - List members (any token, with filtering)
- `GET /members/{member_id}` - Get member by ID (any token)
- `GET /members/guild/{guild_id}` - Get all members of a guild (any token)
- `GET /members/team/{team_id}` - Get all members of a team (any token)
- `PUT /members/{member_id}` - Update member (superuser only)
- `DELETE /members/{member_id}` - Remove member from guild (superuser only)

**Key Features:**
- Member validation (user exists, guild exists, not already a member)
- Team assignment validation
- Guild rank management
- Member status tracking (active/inactive)

## Phase 4: Database Migration
```bash
alembic revision --autogenerate -m "Add members table"
alembic upgrade head
```

## Phase 5: Testing

### Model Tests (`tests/model/test_member_model.py`)
- Member creation and relationships
- Uniqueness constraints (user can only be member of guild once)
- Foreign key constraints
- Cascade deletion
- Soft delete functionality

### Schema Tests (`tests/schema/test_member_schemas.py`)
- Validation rules
- Required fields
- Inheritance and ORM compatibility
- Field constraints

### Feature Tests (`tests/feature/test_member_router.py`)
- CRUD operations
- Authorization (superuser vs regular users)
- Validation and error handling
- Filtering and pagination
- Team assignment logic

## Key Design Decisions

### 1. **Member vs User Relationship**
- **Member** = Guild-specific profile for a User
- **User** = Authentication account (can have multiple memberships)
- One User can be a Member of multiple Guilds

### 2. **Team Assignment**
- Members can optionally be assigned to Teams
- Team assignment is guild-specific
- Members can change teams within their guild

### 3. **Guild Ranks**
- Simple string-based rank system
- Default rank: "Member"
- Common ranks: "Guild Master", "Officer", "Member", "Recruit"

### 4. **Member Status**
- `is_active` flag for soft deletion
- Tracks join date for member history
- Allows for member reactivation

### 5. **Validation Rules**
- User can only be member of a guild once
- Team must belong to the same guild as member
- Display name should be unique within guild (optional)

## Future Integration Points

### Toons System (Next Phase)
- Members will have multiple Toons (characters)
- Toons will link to Members, not directly to Users
- This allows for character management per guild

### Raid System (Future)
- Members participate in raids
- Attendance tracking will link to Members
- Team assignments affect raid organization

### Invite System (Future)
- Invites will create Members when accepted
- Member creation will be part of invite flow

## Implementation Order

1. **Phase 1**: Database models and relationships
2. **Phase 2**: Pydantic schemas with validation
3. **Phase 3**: API router with full CRUD operations
4. **Phase 4**: Database migration
5. **Phase 5**: Comprehensive test suite
6. **Documentation**: Update README with Members endpoints

This plan follows the same patterns established by the Teams implementation and provides a solid foundation for the upcoming Toons and Raid systems.