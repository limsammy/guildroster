# Updated GuildRoster Implementation Plan

## Overview
This plan implements a subscription-based guild management system with role-based permissions, using direct User-Guild-Team relationships where regular users belong to one guild, but admin accounts can view and manage all guilds.

## Phase 1: Core Database & Permission System (Weeks 1-4)

### Week 1: Database Schema Updates

#### 1.1 Update User Model (`app/models/user.py`)
```python
# Add new fields
email = Column(String, unique=True, nullable=True)  # For Stripe integration
is_admin = Column(Boolean, default=False, nullable=False)  # Special admin privileges
guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)
stripe_customer_id = Column(String(100), nullable=True)

# Add relationships
guild = relationship("Guild", back_populates="members")
teams = relationship("Team", secondary="user_teams", back_populates="members")
team_leadership = relationship("Team", foreign_keys="Team.leader_id", back_populates="leader")
```

#### 1.2 Create User-Team Junction Table (`app/models/user_team.py`)
```python
class UserTeam(Base):
    __tablename__ = "user_teams"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_user_team"),
    )
```

#### 1.3 Update Team Model (`app/models/team.py`)
```python
# Add team leader relationship
leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
leader = relationship("User", foreign_keys=[leader_id], back_populates="team_leadership")
members = relationship("User", secondary="user_teams", back_populates="teams")
```

#### 1.4 Update Guild Model (`app/models/guild.py`)
```python
# Add subscription and superuser flags
subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
is_superuser_created = Column(Boolean, default=False, nullable=False)
members = relationship("User", back_populates="guild")
subscription = relationship("Subscription", back_populates="guild")
```

#### 1.5 Create Database Migration
```bash
alembic revision --autogenerate -m "Update user guild team relationships"
alembic upgrade head
```

### Week 2: Permission System Implementation

#### 2.1 Create Permission System (`app/utils/permissions.py`)
```python
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.utils.auth import require_user
from app.utils.logger import get_logger

logger = get_logger(__name__)

def require_guild_member(guild_id: int):
    """Require user to be a member of the specified guild."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Admin users can access any guild
        if current_user.is_admin:
            return current_user
        
        if current_user.guild_id != guild_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of this guild to perform this action"
            )
        return current_user
    return dependency

def require_team_member(team_id: int):
    """Require user to be a member of the specified team."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Admin users can access any team
        if current_user.is_admin:
            return current_user
        
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team or current_user not in team.members:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of this team to perform this action"
            )
        return current_user
    return dependency

def require_team_leader(team_id: int):
    """Require user to be the leader of the specified team."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Admin users can access any team
        if current_user.is_admin:
            return current_user
        
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team or team.leader_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be the team leader to perform this action"
            )
        return current_user
    return dependency

def require_guild_master(guild_id: int):
    """Require user to be the guild master (creator) of the specified guild."""
    def dependency(
        current_user: User = Depends(require_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Admin users can access any guild
        if current_user.is_admin:
            return current_user
        
        guild = db.query(Guild).filter(Guild.id == guild_id).first()
        if not guild or guild.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be the guild master to perform this action"
            )
        return current_user
    return dependency

def require_admin():
    """Require user to be an admin."""
    def dependency(current_user: User = Depends(require_user)) -> User:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    return dependency
```

#### 2.2 Update Auth Utils (`app/utils/auth.py`)
```python
# Add imports for new permission functions
from app.utils.permissions import (
    require_guild_member,
    require_team_member,
    require_team_leader,
    require_guild_master,
    require_admin
)
```

### Week 3: API Endpoint Migration

#### 3.1 Update Guild Router (`app/routers/guild.py`)
```python
# Change guild update/delete to require guild master
@router.put("/{guild_id}", response_model=GuildResponse)
def update_guild(
    guild_id: int,
    guild_data: GuildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_guild_master(guild_id)),
):
    """Update guild (guild master or admin only)."""

@router.delete("/{guild_id}")
def delete_guild(
    guild_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_guild_master(guild_id)),
):
    """Delete guild (guild master or admin only)."""

# Add admin-specific endpoint for viewing all guilds
@router.get("/admin/all", response_model=List[GuildResponse])
def get_all_guilds_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all guilds (admin only)."""
    guilds = db.query(Guild).offset(skip).limit(limit).all()
    return guilds
```

#### 3.2 Update Team Router (`app/routers/team.py`)
```python
# Change team operations to require team leader or guild master
@router.post("/", response_model=TeamResponse)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_guild_member(team_data.guild_id)),
):
    """Create new team (guild member or admin only)."""

@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_team_leader(team_id)),
):
    """Update team (team leader or admin only)."""

@router.delete("/{team_id}")
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_team_leader(team_id)),
):
    """Delete team (team leader or admin only)."""

# Add admin-specific endpoint for viewing all teams
@router.get("/admin/all", response_model=List[TeamResponse])
def get_all_teams_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all teams (admin only)."""
    teams = db.query(Team).offset(skip).limit(limit).all()
    return teams
```

#### 3.3 Update Other Routers
- **Toon Router**: Change to `require_team_member(team_id)` (admin can access all)
- **Raid Router**: Change to `require_team_member(team_id)` (admin can access all)
- **Attendance Router**: Change to `require_team_member(team_id)` (admin can access all)
- **Keep superuser-only**: Token, User, Scenario, Invite routers

#### 3.4 Create Admin Router (`app/routers/admin.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.subscription import Subscription
from app.utils.auth import require_admin
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin dashboard with overview of all guilds and subscriptions."""
    total_guilds = db.query(Guild).count()
    total_users = db.query(User).count()
    active_subscriptions = db.query(Subscription).filter(Subscription.status == "active").count()
    
    return {
        "total_guilds": total_guilds,
        "total_users": total_users,
        "active_subscriptions": active_subscriptions,
        "recent_guilds": db.query(Guild).order_by(Guild.created_at.desc()).limit(5).all()
    }

@router.get("/analytics")
def admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin analytics across all guilds."""
    # Implementation for cross-guild analytics
    pass

@router.get("/subscriptions")
def admin_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """View all subscriptions (admin only)."""
    subscriptions = db.query(Subscription).all()
    return {"subscriptions": subscriptions}
```

### Week 4: Testing & Validation
- Update all existing tests
- Create new permission tests
- Integration testing
- End-to-end testing

## Phase 2: Subscription System (Weeks 5-8)

### Week 5: Subscription Database & Models

#### 5.1 Create Subscription Model (`app/models/subscription.py`)
```python
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)
    
    # Subscription details
    plan_type = Column(String(20), nullable=False)  # "trial", "basic", "premium", "enterprise"
    status = Column(String(20), default="active")  # "active", "cancelled", "expired", "pending"
    monthly_fee = Column(Integer, nullable=False)  # Fee in cents
    billing_cycle = Column(String(10), default="monthly")  # "monthly", "annual"
    
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
    
    __table_args__ = (
        UniqueConstraint("user_id", "guild_id", name="uq_user_guild_subscription"),
    )
```

#### 5.2 Update Configuration (`app/config.py`)
```python
SUBSCRIPTION_PLANS = {
    "trial": {
        "name": "Free Trial",
        "monthly_fee": 0,
        "max_guilds": 1,
        "max_teams": 3,
        "max_members": 75,
        "duration_days": 90,  # 3 months
        "features": ["all_core_features"]
    },
    "basic": {
        "name": "Basic Plan",
        "monthly_fee": 499,  # $4.99
        "annual_fee": 4990,  # $49.90 (2 months free)
        "max_guilds": 1,
        "max_teams": 3,
        "max_members": 75,
        "features": ["all_core_features"]
    },
    "premium": {
        "name": "Premium Plan",
        "monthly_fee": 999,  # $9.99
        "annual_fee": 9990,  # $99.90 (2 months free)
        "max_guilds": 5,  # Contact for more
        "max_teams": -1,  # Unlimited
        "max_members": -1,  # Unlimited
        "features": ["all_core_features", "discord_integration", "advanced_analytics"]
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "monthly_fee": 1999,  # $19.99
        "annual_fee": 19990,  # $199.90 (2 months free)
        "max_guilds": 10,  # Contact for more
        "max_teams": -1,  # Unlimited
        "max_members": -1,  # Unlimited
        "features": ["all_features", "custom_branding", "custom_domain", "priority_support"]
    }
}

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_IDS = {
    "basic_monthly": os.getenv("STRIPE_BASIC_MONTHLY_PRICE_ID"),
    "basic_annual": os.getenv("STRIPE_BASIC_ANNUAL_PRICE_ID"),
    "premium_monthly": os.getenv("STRIPE_PREMIUM_MONTHLY_PRICE_ID"),
    "premium_annual": os.getenv("STRIPE_PREMIUM_ANNUAL_PRICE_ID"),
    "enterprise_monthly": os.getenv("STRIPE_ENTERPRISE_MONTHLY_PRICE_ID"),
    "enterprise_annual": os.getenv("STRIPE_ENTERPRISE_ANNUAL_PRICE_ID"),
}
```

### Week 6: Stripe Integration

#### 6.1 Create Payment Service (`app/utils/payments.py`)
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
    async def create_subscription(user: User, plan_type: str, billing_cycle: str, guild_name: str) -> dict:
        """Create a new subscription."""
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
            
            # Get price ID based on plan and billing cycle
            price_id = settings.STRIPE_PRICE_IDS[f"{plan_type}_{billing_cycle}"]
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{"price": price_id}],
                metadata={
                    "user_id": user.id,
                    "plan_type": plan_type,
                    "billing_cycle": billing_cycle,
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
    async def handle_webhook(event: dict) -> bool:
        """Handle Stripe webhook events."""
        try:
            if event["type"] == "invoice.payment_failed":
                # Handle failed payment
                subscription_id = event["data"]["object"]["subscription"]
                await PaymentService.handle_failed_payment(subscription_id)
            elif event["type"] == "customer.subscription.deleted":
                # Handle subscription cancellation
                subscription_id = event["data"]["object"]["id"]
                await PaymentService.handle_subscription_cancelled(subscription_id)
            
            return True
        except Exception as e:
            logger.error(f"Webhook handling failed: {str(e)}")
            return False
```

#### 6.2 Create Subscription Router (`app/routers/subscription.py`)
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
from app.utils.auth import require_user, require_admin
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

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    success = await PaymentService.handle_webhook(event)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Webhook processing failed")
```

### Week 7: Guild Creation Integration

#### 7.1 Update Guild Creation (`app/routers/guild.py`)
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
    
    if plan_config["max_guilds"] > 0 and existing_guilds >= plan_config["max_guilds"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guild limit reached for your subscription plan"
        )
    
    # Create guild
    guild = Guild(
        name=guild_data.name,
        created_by=current_user.id,
        subscription_id=active_subscription.id,
        is_superuser_created=False
    )
    
    db.add(guild)
    db.commit()
    db.refresh(guild)
    
    # Update subscription with guild_id
    active_subscription.guild_id = guild.id
    db.commit()
    
    return guild
```

### Week 8: Testing & Validation
- Test subscription creation flow
- Test payment processing
- Test webhook handling
- Test guild creation with subscription validation

## Phase 3: Advanced Features (Weeks 9-12)

### Week 9-10: Discord Integration
- Discord OAuth2 authentication
- Raid Helper bot integration
- Sync existing Discord raids
- User authentication via Discord

### Week 11: Advanced Analytics
- Guild awards system
- Log analysis features
- Custom report generation
- Performance analytics

### Week 12: Enterprise Features
- Custom branding
- Custom domain setup
- Priority support system
- API access

## Phase 4: Polish & Launch (Weeks 13-16)

### Week 13-14: Documentation & Onboarding
- Comprehensive documentation with screenshots
- Embedded tutorial videos
- Interactive help system
- Feature tours

### Week 15: Performance & Security
- Performance optimization
- Security audit
- GDPR compliance implementation
- Rate limiting

### Week 16: Production Deployment
- Production environment setup
- Monitoring implementation
- Backup systems
- Launch preparation

## Data Migration Strategy

### Existing User Migration
```python
# Migration script to handle existing users
def migrate_existing_users(db: Session):
    """Migrate existing users to new permission system."""
    
    # Assign all existing superusers to Guild ID 1 (except admin)
    guild_1 = db.query(Guild).filter(Guild.id == 1).first()
    if not guild_1:
        # Create Guild 1 if it doesn't exist
        guild_1 = Guild(
            name="Default Guild",
            created_by=1,  # Admin user ID
            is_superuser_created=True
        )
        db.add(guild_1)
        db.commit()
    
    # Update all existing users to belong to Guild 1
    users = db.query(User).filter(User.guild_id.is_(None)).all()
    for user in users:
        if not user.is_admin:  # Don't change admin user
            user.guild_id = guild_1.id
            user.is_superuser = False  # Downgrade superusers to regular users
    
    db.commit()
```

### Subscription Migration
```python
# Create free trial subscriptions for existing guilds
def create_trial_subscriptions(db: Session):
    """Create trial subscriptions for existing guilds."""
    
    existing_guilds = db.query(Guild).filter(Guild.subscription_id.is_(None)).all()
    for guild in existing_guilds:
        if guild.is_superuser_created:
            # Superuser-created guilds get free access
            subscription = Subscription(
                user_id=guild.created_by,
                guild_id=guild.id,
                plan_type="trial",
                status="active",
                monthly_fee=0,
                expires_at=datetime.now() + timedelta(days=365*10)  # 10 years
            )
            db.add(subscription)
            guild.subscription_id = subscription.id
    
    db.commit()
```

## Success Criteria

### Technical Success
- All endpoints migrated to new permission system
- Subscription system fully functional
- Payment processing working correctly
- No data loss during migration

### Business Success
- Successful trial to paid conversion
- Positive user feedback
- Stable revenue generation
- Growing user base

This updated plan provides a clear path to implementing the subscription-based guild management system with proper role-based permissions and comprehensive feature set. 