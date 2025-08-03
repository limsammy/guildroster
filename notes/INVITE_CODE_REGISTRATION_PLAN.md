# Invite Code Registration Feature Implementation Plan

## Overview
Implement a secure invite code system that allows superusers to generate invite codes for new user registration. Users can manage their generated codes, track usage, and invalidate unused codes.

## Feature Requirements

### Core Functionality
- ✅ Superusers can generate invite codes
- ✅ New users can register using valid invite codes
- ✅ Users can view their generated invite codes
- ✅ Users can see which codes have been used and by whom
- ✅ Users can invalidate unused invite codes
- ✅ Invite codes expire after 1 week (configurable)

### Technical Specifications

#### Invite Code Format
- **Length**: 8 characters
- **Characters**: Alphanumeric (A-Z, 0-9) uppercase only
- **Generation**: Cryptographically secure random using `secrets` module
- **Display**: Always shown in uppercase for readability
- **Validation**: Case-insensitive input, stored as uppercase

#### Expiration Settings
- **Default**: 1 week from creation
- **Option**: No expiration (for special cases)
- **Storage**: `expires_at` timestamp field

#### Usage Limits
- **Single-use only**: Each code can only be used once
- **Status tracking**: Track used/unused status
- **User association**: Link used codes to registered users

## Database Schema

### New Invite Model (`app/models/invite.py`)
```python
class Invite(Base):
    __tablename__ = "invites"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # NULL = no expiration
    created_at = Column(DateTime, default=datetime.now)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_invites")
    used_user = relationship("User", foreign_keys=[used_by], back_populates="used_invite")
```

### Updated User Model (`app/models/user.py`)
```python
# Add these relationships to existing User model
created_invites = relationship("Invite", foreign_keys="Invite.created_by", back_populates="creator")
used_invite = relationship("Invite", foreign_keys="Invite.used_by", back_populates="used_user")
```

## API Endpoints

### New Invite Router (`app/routers/invite.py`)

#### Generate Invite Code
```python
@router.post("/", response_model=InviteResponse)
def create_invite(
    expires_in_days: Optional[int] = 7,  # None = no expiration
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Generate a new invite code (superuser only).
    
    **Parameters:**
    - `expires_in_days`: Days until expiration (None for no expiration)
    
    **Authentication:**
    - Requires superuser token
    """
```

#### List User's Invite Codes
```python
@router.get("/", response_model=InviteListResponse)
def get_invites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all invite codes created by the current user.
    
    **Authentication:**
    - Requires user token
    """
```

#### Invalidate Invite Code
```python
@router.delete("/{invite_id}")
def invalidate_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Invalidate an unused invite code.
    
    **Authentication:**
    - Requires user token (can only invalidate own codes)
    """
```

### Updated User Router (`app/routers/user.py`)

#### User Registration with Invite Code
```python
@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db),
):
    """
    Register a new user using an invite code.
    
    **Authentication:**
    - No authentication required (public endpoint)
    """
```

## Pydantic Schemas

### New Invite Schemas (`app/schemas/invite.py`)
```python
class InviteBase(BaseModel):
    code: str
    is_active: bool
    expires_at: Optional[datetime] = None

class InviteCreate(BaseModel):
    expires_in_days: Optional[int] = Field(7, ge=1, le=365, description="Days until expiration (None for no expiration)")

class InviteResponse(InviteBase):
    id: int
    created_by: int
    used_by: Optional[int] = None
    created_at: datetime
    used_at: Optional[datetime] = None
    creator_username: Optional[str] = None
    used_username: Optional[str] = None
    is_expired: bool

class InviteListResponse(BaseModel):
    invites: List[InviteResponse]
    total: int
    unused_count: int
    used_count: int
    expired_count: int
```

### Updated User Schemas (`app/schemas/user.py`)
```python
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    invite_code: str = Field(..., min_length=8, max_length=8, description="8-character invite code")
```

## Utility Functions

### Invite Code Utilities (`app/utils/invite.py`)
```python
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.invite import Invite
from app.models.user import User

def generate_invite_code() -> str:
    """Generate a cryptographically secure 8-character alphanumeric code."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))

def validate_invite_code(code: str, db: Session) -> Invite:
    """Validate an invite code and return the invite object."""
    # Normalize to uppercase
    code = code.upper()
    
    invite = db.query(Invite).filter(Invite.code == code).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    
    if not invite.is_active:
        raise HTTPException(status_code=400, detail="Invite code has been invalidated")
    
    if invite.used_by is not None:
        raise HTTPException(status_code=400, detail="Invite code has already been used")
    
    if invite.expires_at and invite.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invite code has expired")
    
    return invite

def use_invite_code(code: str, user_id: int, db: Session) -> None:
    """Mark an invite code as used by a specific user."""
    invite = validate_invite_code(code, db)
    invite.used_by = user_id
    invite.used_at = datetime.now()
    db.commit()

def is_invite_expired(invite: Invite) -> bool:
    """Check if an invite code has expired."""
    if not invite.expires_at:
        return False
    return invite.expires_at < datetime.now()
```

## Frontend Implementation

### New Invite Management Page (`frontend/app/routes/invites.tsx`)
- **Generate Codes**: Button for superusers to create new codes
- **Code List**: Table showing all generated codes with status
- **Usage Tracking**: Show which codes are used and by whom
- **Invalidation**: Button to invalidate unused codes
- **Expiration**: Show expiration dates and expired status
- **Search/Filter**: Filter by status (used/unused/expired)

### Updated Registration Flow
- **Invite Code Field**: Required field in registration form
- **Real-time Validation**: Check code validity as user types
- **Error Handling**: Clear error messages for invalid codes
- **Success Flow**: Redirect to login after successful registration

### API Integration (`frontend/app/api/invites.ts`)
```typescript
// Generate new invite code
export const createInvite = async (expiresInDays?: number): Promise<InviteResponse>

// Get user's invite codes
export const getInvites = async (skip?: number, limit?: number): Promise<InviteListResponse>

// Invalidate invite code
export const invalidateInvite = async (inviteId: number): Promise<void>

// Register user with invite code
export const registerUser = async (userData: UserRegistration): Promise<UserResponse>
```

## Security Considerations

### Code Generation Security
- Use `secrets` module for cryptographically secure randomness
- Ensure codes are unique (check database before returning)
- Rate limiting on code generation (max 10 codes per hour per user)

### Validation Security
- Server-side validation of all invite codes
- Case-insensitive input handling
- Proper error messages without information leakage

### Access Control
- Only superusers can generate codes
- Users can only see and manage their own generated codes
- Public registration endpoint with invite code validation

### Rate Limiting
- Registration endpoint: 5 attempts per hour per IP
- Code generation: 10 codes per hour per user
- Code validation: 20 attempts per hour per IP

## Implementation Steps

### Phase 1: Backend Foundation
1. Create database models and run migrations
2. Implement utility functions for code generation and validation
3. Create Pydantic schemas
4. Implement invite router endpoints
5. Add registration endpoint to user router
6. Update user model relationships

### Phase 2: Frontend Implementation
1. Create invite management page
2. Implement API integration functions
3. Update registration flow with invite code validation
4. Add navigation and routing

### Phase 3: Testing & Polish
1. Write comprehensive tests for all endpoints
2. Add error handling and validation
3. Implement rate limiting
4. Update documentation
5. Add logging and monitoring

## Database Migration

### New Migration File
```python
"""Add invite codes table

Revision ID: xxx
Revises: xxx
Create Date: 2024-01-XX

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(8), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('used_by', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['used_by'], ['users.id']),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_invites_code', 'invites', ['code'])
    op.create_index('ix_invites_created_by', 'invites', ['created_by'])

def downgrade():
    op.drop_table('invites')
```

## Testing Strategy

### Unit Tests
- Code generation utility functions
- Invite validation logic
- Schema validation
- Database model relationships

### Integration Tests
- API endpoint functionality
- Database operations
- Authentication and authorization
- Error handling

### End-to-End Tests
- Complete registration flow
- Invite code management
- Frontend-backend integration

## Future Enhancements

### Potential Improvements
- **Bulk Operations**: Generate multiple codes at once
- **Code Templates**: Predefined code patterns
- **Usage Analytics**: Track code usage patterns
- **Email Integration**: Send codes via email
- **QR Codes**: Generate QR codes for easy sharing
- **Code Categories**: Different types of invite codes
- **Audit Logging**: Track all invite code operations

### Configuration Options
- **Default Expiration**: Configurable default expiration time
- **Code Length**: Configurable code length
- **Character Set**: Configurable character set for codes
- **Rate Limits**: Configurable rate limiting settings

## Notes

- All invite codes are stored in uppercase for consistency
- Expired codes are still tracked but marked as expired
- Used codes cannot be invalidated (already consumed)
- Users can only manage codes they created
- Registration endpoint is public but requires valid invite code
- All operations are logged for audit purposes 