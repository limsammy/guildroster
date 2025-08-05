# GuildRoster Migration Plan: From Superuser-Only to User-Based Permissions

## Current State Analysis

The application currently uses a superuser-only model where:
- All CRUD operations require `require_superuser` authentication
- Users can only be superusers or regular users (no role-based permissions)
- No guild/team membership system exists
- Users are not associated with specific guilds or teams

## Migration Plan Overview

### Phase 1: Database Schema Changes
### Phase 2: Authentication & Authorization System
### Phase 3: API Endpoint Migration
### Phase 4: Testing & Validation
### Phase 5: Documentation & Deployment

---

## Phase 1: Database Schema Changes

### 1.1 Create Member Model
**File:** `app/models/member.py`

```python
class Member(Base):
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
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
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "guild_id", name="uq_user_guild"),
    )
```

### 1.2 Update Existing Models

**User Model Updates** (`app/models/user.py`):
```python
# Add relationship
memberships = relationship("Member", back_populates="user", cascade="all, delete-orphan")
```

**Guild Model Updates** (`app/models/guild.py`):
```python
# Add relationship
members = relationship("Member", back_populates="guild", cascade="all, delete-orphan")
```

**Team Model Updates** (`app/models/team.py`):
```python
# Add relationship
members = relationship("Member", back_populates="team", cascade="all, delete-orphan")
```

**Toon Model Updates** (`app/models/toon.py`):
```python
# Replace user_id with member_id
member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
member = relationship("Member", back_populates="toons")
```

### 1.3 Create Database Migration
```bash
alembic revision --autogenerate -m "Add members table and update relationships"
alembic upgrade head
```

---

## Phase 2: Authentication & Authorization System

### 2.1 Create Permission System
**File:** `app/utils/permissions.py`

```python
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.member import Member
from app.models.guild import Guild
from app.models.team import Team
from app.utils.auth import require_user
from app.utils.logger import get_logger

logger = get_logger(__name__)

def get_user_memberships(user: User, db: Session) -> List[Member]:
    """Get all guild memberships for a user."""
    return db.query(Member).filter(
        Member.user_id == user.id,
        Member.is_active == True
    ).all()

def get_user_guild_membership(user: User, guild_id: int, db: Session) -> Optional[Member]:
    """Get user's membership in a specific guild."""
    return db.query(Member).filter(
        Member.user_id == user.id,
        Member.guild_id == guild_id,
        Member.is_active == True
    ).first()

def get_user_team_membership(user: User, team_id: int, db: Session) -> Optional[Member]:
    """Get user's membership in a specific team."""
    return db.query(Member).filter(
        Member.user_id == user.id,
        Member.team_id == team_id,
        Member.is_active == True
    ).first()

def require_guild_member(guild_id: int):
    """Require user to be a member of the specified guild."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> Member:
        membership = get_user_guild_membership(current_user, guild_id, db)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of this guild to perform this action"
            )
        return membership
    return dependency

def require_team_member(team_id: int):
    """Require user to be a member of the specified team."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> Member:
        membership = get_user_team_membership(current_user, team_id, db)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of this team to perform this action"
            )
        return membership
    return dependency

def require_guild_officer(guild_id: int):
    """Require user to be an officer or guild master of the specified guild."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> Member:
        membership = get_user_guild_membership(current_user, guild_id, db)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of this guild to perform this action"
            )
        
        if membership.rank not in ["Guild Master", "Officer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be an officer or guild master to perform this action"
            )
        return membership
    return dependency

def require_guild_master(guild_id: int):
    """Require user to be the guild master of the specified guild."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> Member:
        membership = get_user_guild_membership(current_user, guild_id, db)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of this guild to perform this action"
            )
        
        if membership.rank != "Guild Master":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be the guild master to perform this action"
            )
        return membership
    return dependency
```

### 2.2 Update Auth Utils
**File:** `app/utils/auth.py`

Add new permission functions:
```python
# Add imports for new permission functions
from app.utils.permissions import (
    require_guild_member,
    require_team_member,
    require_guild_officer,
    require_guild_master
)
```

---

## Phase 3: API Endpoint Migration

### 3.1 Create Member Router
**File:** `app/routers/member.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.schemas.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
)
from app.utils.auth import require_user, require_superuser
from app.utils.permissions import require_guild_officer, require_guild_master
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/members",
    tags=["members"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=MemberResponse)
def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),  # Initially superuser only
):
    """Add a user to a guild (superuser only initially)."""
    # Implementation here

@router.get("/", response_model=MemberListResponse)
def list_members(
    guild_id: Optional[int] = None,
    team_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """List members with optional filtering."""
    # Implementation here

@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get member by ID."""
    # Implementation here

@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    member_data: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),  # Initially superuser only
):
    """Update member (superuser only initially)."""
    # Implementation here

@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),  # Initially superuser only
):
    """Remove member from guild (superuser only initially)."""
    # Implementation here
```

### 3.2 Update Existing Routers

#### Guild Router Updates (`app/routers/guild.py`)
**Current superuser endpoints to change:**
- `POST /guilds/` - Keep superuser only (guild creation) - **Phase 1**
- `PUT /guilds/{guild_id}` - Change to `require_guild_master(guild_id)`
- `DELETE /guilds/{guild_id}` - Change to `require_guild_master(guild_id)`

**Future Phase - Subscription System:**
- `POST /guilds/` - Change to subscription-based guild creation (Phase 2)

#### Team Router Updates (`app/routers/team.py`)
**Current superuser endpoints to change:**
- `POST /teams/` - Change to `require_guild_officer(guild_id)` (from request body)
- `PUT /teams/{team_id}` - Change to `require_guild_officer(team.guild_id)`
- `DELETE /teams/{team_id}` - Change to `require_guild_officer(team.guild_id)`

#### Toon Router Updates (`app/routers/toon.py`)
**Current superuser endpoints to change:**
- `POST /toons/` - Change to `require_team_member(team_id)` (from request body)
- `PUT /toons/{toon_id}` - Change to `require_team_member(toon.team_id)`
- `DELETE /toons/{toon_id}` - Change to `require_team_member(toon.team_id)`

#### Raid Router Updates (`app/routers/raid.py`)
**Current superuser endpoints to change:**
- `POST /raids/` - Change to `require_team_member(team_id)` (from request body)
- `PUT /raids/{raid_id}` - Change to `require_team_member(raid.team_id)`
- `DELETE /raids/{raid_id}` - Change to `require_team_member(raid.team_id)`

#### Attendance Router Updates (`app/routers/attendance.py`)
**Current superuser endpoints to change:**
- `POST /attendance/` - Change to `require_team_member(raid.team_id)` (from raid lookup)
- `POST /attendance/bulk` - Change to `require_team_member(raid.team_id)` (from raid lookup)
- `PUT /attendance/{attendance_id}` - Change to `require_team_member(attendance.raid.team_id)`
- `PUT /attendance/bulk` - Change to `require_team_member(raid.team_id)` (from raid lookup)
- `DELETE /attendance/{attendance_id}` - Change to `require_team_member(attendance.raid.team_id)`

#### Scenario Router Updates (`app/routers/scenario.py`)
**Current superuser endpoints to change:**
- `POST /scenarios/` - Keep superuser only (global scenarios)
- `PUT /scenarios/{scenario_id}` - Keep superuser only (global scenarios)
- `DELETE /scenarios/{scenario_id}` - Keep superuser only (global scenarios)

#### Token Router Updates (`app/routers/token.py`)
**Current superuser endpoints to change:**
- All token management - Keep superuser only (system-wide)

#### User Router Updates (`app/routers/user.py`)
**Current superuser endpoints to change:**
- `POST /users/` - Keep superuser only (user creation)
- `PUT /users/{id}` - Keep superuser only (user management)
- `DELETE /users/{id}` - Keep superuser only (user management)

### 3.3 Detailed Endpoint Migration Examples

#### Example: Guild Update Endpoint
**Before:**
```python
@router.put("/{guild_id}", response_model=GuildResponse)
def update_guild(
    guild_id: int,
    guild_data: GuildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),  # OLD
):
```

**After:**
```python
@router.put("/{guild_id}", response_model=GuildResponse)
def update_guild(
    guild_id: int,
    guild_data: GuildUpdate,
    db: Session = Depends(get_db),
    current_member: Member = Depends(require_guild_master(guild_id)),  # NEW
):
    """Update guild (guild master only)."""
    # Implementation remains the same
```

#### Example: Team Creation Endpoint
**Before:**
```python
@router.post("/", response_model=TeamResponse)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),  # OLD
):
```

**After:**
```python
@router.post("/", response_model=TeamResponse)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_member: Member = Depends(require_guild_officer(team_data.guild_id)),  # NEW
):
    """Create new team (guild officer or master only)."""
    # Implementation remains the same
```

---

## Phase 4: Testing & Validation

### 4.1 Create Member Model Tests
**File:** `tests/model/test_member_model.py`

### 4.2 Create Permission Tests
**File:** `tests/unit/test_permissions.py`

### 4.3 Update Existing Router Tests
Update all router tests to use new permission system instead of superuser checks.

### 4.4 Create Integration Tests
**File:** `tests/feature/test_permission_system.py`

---

## Phase 5: Implementation Steps

### Step 1: Database Changes
1. Create Member model
2. Update existing models with relationships
3. Create and run migration
4. Test database changes

### Step 2: Permission System
1. Create permissions utility module
2. Add new permission decorators
3. Test permission functions

### Step 3: Member Router
1. Create Member schemas
2. Create Member router with CRUD operations
3. Test Member endpoints

### Step 4: Router Migration (One at a time)
1. **Guild Router** - Update guild management endpoints
2. **Team Router** - Update team management endpoints  
3. **Toon Router** - Update character management endpoints
4. **Raid Router** - Update raid management endpoints
5. **Attendance Router** - Update attendance management endpoints
6. **Keep superuser-only**: Token, User, Scenario routers

### Step 5: Testing
1. Update all existing tests
2. Create new permission tests
3. Integration testing
4. End-to-end testing

### Step 6: Documentation
1. Update API documentation
2. Update README with new permission system
3. Create migration guide for existing users

---

## Migration Strategy

### Gradual Migration Approach
1. **Phase 1**: Add Member system alongside existing superuser system
2. **Phase 2**: Migrate endpoints one router at a time
3. **Phase 3**: Keep superuser fallback for critical operations
4. **Phase 4**: Eventually deprecate superuser-only endpoints

### Backward Compatibility
- Keep superuser endpoints functional during transition
- Add new permission-based endpoints alongside existing ones
- Provide clear migration path for existing users

### Data Migration
- Create Member records for existing users
- Assign default guild/team memberships
- Preserve existing data relationships

---

## Risk Mitigation

### Rollback Plan
- Keep superuser endpoints functional
- Database migration is reversible
- Feature flags for new permission system

### Testing Strategy
- Comprehensive unit tests for new permission system
- Integration tests for all endpoint changes
- End-to-end testing with real user scenarios

### Documentation
- Clear migration guide for existing users
- Updated API documentation
- Permission system documentation

---

## Current Superuser Usage Analysis

Based on the codebase analysis, here are the current `require_superuser` usages that need to be migrated:

### Routers with Superuser Dependencies:

1. **Guild Router** (`app/routers/guild.py`)
   - `POST /guilds/` - Create guild
   - `PUT /guilds/{guild_id}` - Update guild
   - `DELETE /guilds/{guild_id}` - Delete guild

2. **Team Router** (`app/routers/team.py`)
   - `POST /teams/` - Create team
   - `PUT /teams/{team_id}` - Update team
   - `DELETE /teams/{team_id}` - Delete team

3. **Toon Router** (`app/routers/toon.py`)
   - `POST /toons/` - Create character
   - `PUT /toons/{toon_id}` - Update character
   - `DELETE /toons/{toon_id}` - Delete character

4. **Raid Router** (`app/routers/raid.py`)
   - `POST /raids/` - Create raid
   - `PUT /raids/{raid_id}` - Update raid
   - `DELETE /raids/{raid_id}` - Delete raid

5. **Attendance Router** (`app/routers/attendance.py`)
   - `POST /attendance/` - Create attendance record
   - `POST /attendance/bulk` - Bulk create attendance
   - `PUT /attendance/{attendance_id}` - Update attendance
   - `PUT /attendance/bulk` - Bulk update attendance
   - `DELETE /attendance/{attendance_id}` - Delete attendance

6. **Scenario Router** (`app/routers/scenario.py`)
   - `POST /scenarios/` - Create scenario
   - `PUT /scenarios/{scenario_id}` - Update scenario
   - `DELETE /scenarios/{scenario_id}` - Delete scenario

7. **Token Router** (`app/routers/token.py`)
   - All CRUD operations (keep superuser only)

8. **User Router** (`app/routers/user.py`)
   - `POST /users/` - Create user
   - `PUT /users/{id}` - Update user
   - `DELETE /users/{id}` - Delete user

9. **Invite Router** (`app/routers/invite.py`)
   - `POST /invites/` - Create invite (keep superuser only)

---

## Permission Hierarchy

### Guild Ranks:
1. **Guild Master** - Full control over guild and all teams
2. **Officer** - Can manage teams and members within guild
3. **Member** - Can manage their own characters and raid attendance
4. **Recruit** - Read-only access to guild information

### Permission Matrix:

| Action | Guild Master | Officer | Member | Recruit |
|--------|-------------|---------|--------|---------|
| Create Guild | ❌ | ❌ | ❌ | ❌ |
| Update Guild | ✅ | ❌ | ❌ | ❌ |
| Delete Guild | ✅ | ❌ | ❌ | ❌ |
| Create Invite | ❌ | ❌ | ❌ | ❌ |
| Create Team | ✅ | ✅ | ❌ | ❌ |
| Update Team | ✅ | ✅ | ❌ | ❌ |
| Delete Team | ✅ | ✅ | ❌ | ❌ |
| Create Character | ✅ | ✅ | ✅ | ❌ |
| Update Character | ✅ | ✅ | ✅ | ❌ |
| Delete Character | ✅ | ✅ | ✅ | ❌ |
| Create Raid | ✅ | ✅ | ✅ | ❌ |
| Update Raid | ✅ | ✅ | ✅ | ❌ |
| Delete Raid | ✅ | ✅ | ✅ | ❌ |
| Manage Attendance | ✅ | ✅ | ✅ | ❌ |
| View Guild Info | ✅ | ✅ | ✅ | ✅ |
| View Team Info | ✅ | ✅ | ✅ | ✅ |

---

## Implementation Timeline

### Week 1: Foundation
- Database schema changes
- Permission system implementation
- Basic Member router

### Week 2: Core Migration
- Guild router migration
- Team router migration
- Toon router migration

### Week 3: Advanced Features
- Raid router migration
- Attendance router migration
- Integration testing

### Week 4: Polish & Deploy
- Documentation updates
- End-to-end testing
- Production deployment

---

## Phase 6: Subscription-Based Guild Creation System

### 6.1 Subscription System Overview
The application will evolve to support public guild creation through a subscription model where users can pay a monthly fee to create and manage their own guilds.

### 6.2 Database Schema for Subscriptions

#### Subscription Model (`app/models/subscription.py`)
```python
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)  # Null during creation
    
    # Subscription details
    plan_type = Column(String(20), nullable=False)  # "basic", "premium", "enterprise"
    status = Column(String(20), default="active")  # "active", "cancelled", "expired", "pending"
    monthly_fee = Column(Integer, nullable=False)  # Fee in cents
    
    # Billing information
    stripe_subscription_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    guild = relationship("Guild", back_populates="subscription")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "guild_id", name="uq_user_guild_subscription"),
    )
```

#### Update User Model (`app/models/user.py`)
```python
# Add subscription relationship
subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
```

#### Update Guild Model (`app/models/guild.py`)
```python
# Add subscription relationship
subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
subscription = relationship("Subscription", back_populates="guild")
```

### 6.3 Subscription Plans

#### Plan Configuration (`app/config.py`)
```python
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic Guild",
        "monthly_fee": 999,  # $9.99
        "max_teams": 3,
        "max_members": 50,
        "features": ["basic_analytics", "raid_tracking", "attendance_reports"]
    },
    "premium": {
        "name": "Premium Guild", 
        "monthly_fee": 1999,  # $19.99
        "max_teams": 10,
        "max_members": 200,
        "features": ["advanced_analytics", "warcraftlogs_integration", "custom_reports", "priority_support"]
    },
    "enterprise": {
        "name": "Enterprise Guild",
        "monthly_fee": 4999,  # $49.99
        "max_teams": 50,
        "max_members": 1000,
        "features": ["all_premium_features", "api_access", "white_label", "dedicated_support"]
    }
}
```

### 6.4 Payment Integration

#### Stripe Integration (`app/utils/payments.py`)
```python
import stripe
from fastapi import HTTPException, status
from app.config import settings
from app.models.subscription import Subscription
from app.models.user import User
from app.models.guild import Guild

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    async def create_subscription(user: User, plan_type: str, guild_name: str) -> dict:
        """Create a new subscription and guild."""
        try:
            # Create Stripe customer if doesn't exist
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=user.username,
                    metadata={"user_id": user.id}
                )
                user.stripe_customer_id = customer.id
                db.commit()
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{"price": settings.STRIPE_PRICE_IDS[plan_type]}],
                metadata={
                    "user_id": user.id,
                    "plan_type": plan_type,
                    "guild_name": guild_name
                }
            )
            
            return {
                "subscription_id": subscription.id,
                "customer_id": user.stripe_customer_id,
                "status": subscription.status
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment processing failed: {str(e)}"
            )
    
    @staticmethod
    async def cancel_subscription(subscription_id: str) -> bool:
        """Cancel a subscription."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return subscription.status == "active"
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
```

### 6.5 Updated Guild Creation Flow

#### Guild Creation Endpoint (`app/routers/guild.py`)
```python
@router.post("/", response_model=GuildResponse)
def create_guild(
    guild_data: GuildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create a new guild (subscription required)."""
    
    # Check if user has active subscription
    active_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not active_subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required to create a guild"
        )
    
    # Check guild limits based on plan
    plan_config = settings.SUBSCRIPTION_PLANS[active_subscription.plan_type]
    existing_guilds = db.query(Guild).filter(
        Guild.subscription_id == active_subscription.id
    ).count()
    
    if existing_guilds >= 1:  # Basic plan allows 1 guild
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guild limit reached for your subscription plan"
        )
    
    # Create guild
    guild = Guild(
        name=guild_data.name,
        created_by=current_user.id,
        subscription_id=active_subscription.id
    )
    
    db.add(guild)
    db.commit()
    db.refresh(guild)
    
    # Update subscription with guild_id
    active_subscription.guild_id = guild.id
    db.commit()
    
    return guild
```

### 6.6 Subscription Management Router

#### Subscription Router (`app/routers/subscription.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionListResponse,
    PlanSelection,
)
from app.utils.auth import require_user, require_superuser
from app.utils.payments import PaymentService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", response_model=dict)
async def create_subscription(
    plan_data: PlanSelection,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create a new subscription for guild creation."""
    # Implementation with Stripe integration

@router.get("/", response_model=SubscriptionListResponse)
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """List user's subscriptions."""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    return {"subscriptions": subscriptions}

@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Cancel a subscription."""
    # Implementation with Stripe integration

@router.get("/plans", response_model=dict)
def get_available_plans():
    """Get available subscription plans."""
    return settings.SUBSCRIPTION_PLANS
```

### 6.7 Frontend Integration

#### Subscription Management UI
- **Plan Selection Page**: Display available plans with features and pricing
- **Payment Form**: Stripe Elements integration for secure payment processing
- **Subscription Dashboard**: Manage active subscriptions, view billing history
- **Guild Creation Flow**: Integrated with subscription verification

#### Key Frontend Components:
```typescript
// Plan selection component
interface Plan {
  name: string;
  monthly_fee: number;
  max_teams: number;
  max_members: number;
  features: string[];
}

// Subscription management
interface Subscription {
  id: number;
  plan_type: string;
  status: string;
  expires_at: string;
  guild_id?: number;
}
```

### 6.8 Implementation Timeline for Subscription System

#### Phase 2A: Foundation (Week 5-6)
- Database schema for subscriptions
- Stripe integration setup
- Basic subscription management

#### Phase 2B: Guild Integration (Week 7-8)
- Update guild creation to require subscription
- Implement plan-based limits
- Subscription validation middleware

#### Phase 2C: Frontend & Billing (Week 9-10)
- Subscription management UI
- Payment processing integration
- Billing dashboard

#### Phase 2D: Testing & Launch (Week 11-12)
- End-to-end testing
- Payment flow testing
- Production deployment

### 6.9 Security & Compliance

#### Payment Security
- PCI DSS compliance through Stripe
- Secure payment processing
- No sensitive payment data stored locally

#### Subscription Validation
- Real-time subscription status checking
- Automatic guild access revocation for expired subscriptions
- Grace period for payment issues

#### Rate Limiting
- Prevent subscription abuse
- Limit guild creation attempts
- Monitor for suspicious activity

### 6.10 Migration Strategy for Existing Users

#### Free Tier for Existing Guilds
- Existing guilds get grandfathered into a free tier
- Limited features but no payment required
- Option to upgrade to paid plans

#### Data Migration
- Preserve existing guild data
- Create subscription records for existing guilds
- Maintain user relationships

This plan provides a comprehensive approach to migrating from superuser-only to a user-based permission system while maintaining system stability and providing a clear path forward for the application. 