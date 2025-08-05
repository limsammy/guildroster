# GuildRoster Application Specifications

## Overview
GuildRoster is a SaaS application for World of Warcraft guild management with subscription-based access and comprehensive raid tracking features.

## Core Architecture

### User Management
- **One Guild Per User**: Regular users can only belong to one guild at a time
- **Admin Multi-Guild Access**: Admin accounts can view and manage all guilds
- **Team Assignments**: Users can belong to multiple teams via junction table
- **Role-Based Permissions**: Admin, Superuser, Guild Master, Team Leader, Member roles

### Database Schema

#### User Model Updates
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)  # For Stripe integration
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)  # Special admin privileges
    
    # Guild and Team relationships (one guild per user for regular users)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    
    # Relationships
    guild = relationship("Guild", back_populates="members")
    teams = relationship("Team", secondary="user_teams", back_populates="members")
    team_leadership = relationship("Team", foreign_keys="Team.leader_id", back_populates="leader")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

#### User-Team Junction Table
```python
class UserTeam(Base):
    __tablename__ = "user_teams"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.now)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_user_team"),
    )
```

#### Team Model Updates
```python
class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, index=True)
    description = Column(String(200), nullable=True)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Team Leader
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    guild = relationship("Guild", back_populates="teams")
    leader = relationship("User", foreign_keys=[leader_id], back_populates="team_leadership")
    members = relationship("User", secondary="user_teams", back_populates="teams")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

#### Guild Model Updates
```python
class Guild(Base):
    __tablename__ = "guilds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    is_superuser_created = Column(Boolean, default=False, nullable=False)  # Exempt from subscription
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("User", back_populates="guild")
    teams = relationship("Team", back_populates="guild", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="guild")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

## Permission System

### Role Hierarchy
1. **Admin** - Full application access, manage all subscriptions, view analytics
2. **Superuser** - System-wide management, create guilds, manage users
3. **Guild Master** - Full control over their guild and all teams
4. **Team Leader** - Manage their assigned teams (can lead multiple teams)
5. **Member** - Basic guild access, manage own characters

### Permission Matrix

| Action | Admin | Superuser | Guild Master | Team Leader | Member |
|--------|-------|-----------|--------------|-------------|--------|
| Create Guild | ✅ | ✅ | ❌ | ❌ | ❌ |
| Update Guild | ✅ | ✅ | ✅ (own) | ❌ | ❌ |
| Delete Guild | ✅ | ✅ | ✅ (own) | ❌ | ❌ |
| View All Guilds | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage All Guilds | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Team | ✅ | ✅ | ✅ | ✅ (own teams) | ❌ |
| Update Team | ✅ | ✅ | ✅ | ✅ (own teams) | ❌ |
| Delete Team | ✅ | ✅ | ✅ | ✅ (own teams) | ❌ |
| Create Character | ✅ | ✅ | ✅ | ✅ | ✅ |
| Update Character | ✅ | ✅ | ✅ | ✅ | ✅ (own) |
| Delete Character | ✅ | ✅ | ✅ | ✅ | ✅ (own) |
| Create Raid | ✅ | ✅ | ✅ | ✅ (own teams) | ✅ |
| Update Raid | ✅ | ✅ | ✅ | ✅ (own teams) | ✅ |
| Delete Raid | ✅ | ✅ | ✅ | ✅ (own teams) | ✅ |
| Manage Attendance | ✅ | ✅ | ✅ | ✅ (own teams) | ✅ |
| Create Invite | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | ✅ (own guild) | ✅ (own teams) | ✅ (own guild) |
| View All Analytics | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage Subscriptions | ✅ | ❌ | ❌ | ❌ | ❌ |

## Subscription System

### Subscription Plans

#### Free Trial (1-3 months)
- **Duration**: 1-3 months (configurable)
- **Guilds**: 1 guild maximum
- **Teams**: 3 teams maximum
- **Members**: 75 members maximum
- **Features**: All core features available
- **Payment**: None required

#### Basic Plan ($4.99/month, $49.90/year)
- **Guilds**: 1 guild maximum
- **Teams**: 3 teams maximum
- **Members**: 75 members maximum
- **Features**: All core features
- **Annual Discount**: 2 months free

#### Premium Plan ($9.99/month, $99.90/year)
- **Guilds**: Multiple guilds (contact for limits)
- **Teams**: Unlimited teams
- **Members**: Unlimited members
- **Features**: All core features + Discord integration
- **Annual Discount**: 2 months free

#### Enterprise Plan ($19.99/month, $199.90/year)
- **Guilds**: Multiple guilds (contact for limits)
- **Teams**: Unlimited teams
- **Members**: Unlimited members
- **Features**: All features + Custom branding, Custom domain, Priority support
- **Annual Discount**: 2 months free

### Payment Processing

#### Stripe Integration
- **Payment Processor**: Stripe
- **Billing Cycle**: Monthly or Annual
- **Failed Payment Handling**: 7-day grace period with email notifications
- **Manual Intervention**: Required for failed payments
- **Trial Period**: 1-3 months free trial

#### Subscription Management
- **Webhook Handling**: Real-time subscription updates
- **Automatic Renewal**: Enabled by default
- **Cancellation**: Immediate or end of billing period
- **Upgrades/Downgrades**: Prorated billing

## Feature Specifications

### Core Features (All Tiers)
- **Guild Management**: Create, update, delete guilds
- **Team Management**: Create, update, delete teams
- **Character Management**: Create, update, delete characters
- **Raid Management**: Schedule and track raids
- **Attendance Tracking**: Comprehensive attendance system
- **WarcraftLogs Integration**: Automatic participant extraction
- **Basic Analytics**: Attendance trends, raid completion rates
- **Export Data**: JSON export functionality
- **Admin Dashboard**: View and manage all guilds (admin only)

### Premium Features ($9.99+)
- **Discord Integration**: 
  - User authentication via Discord
  - Raid Helper bot integration
  - Sync existing Discord raids
- **Advanced Analytics**: Team performance analysis
- **Custom Reports**: Manual report generation

### Enterprise Features ($19.99+)
- **Custom Branding**: White-label options
- **Custom Domain**: Dedicated subdomain setup
- **Priority Support**: Direct support access
- **Advanced Analytics**: Guild awards, log analysis
- **API Access**: REST API for integrations

### Discord Integration Details
- **Authentication**: Login with Discord OAuth2
- **Raid Helper Integration**: 
  - Pull existing raids from Discord
  - Sync attendance data
  - Manage raid scheduling
- **Bot Permissions**: Read guild info, manage events
- **Cloud-Only**: Not available for self-hosted versions

### Analytics & Reports
- **Attendance Trends**: Historical attendance patterns
- **Raid Completion**: Success/failure rates
- **Team Performance**: Team-based analytics
- **Guild Awards**: Fun statistics from logs
  - Most damage dealt
  - Most healing done
  - "Fire stander" awards
  - MVP recognition
- **Manual Reports**: User-triggered report generation
- **Export Formats**: JSON, CSV, PDF

## Technical Requirements

### Security & Compliance
- **GDPR Compliance**: Data export, soft delete, privacy policy
- **PCI DSS**: Stripe handles payment security
- **Authentication**: Secure password hashing (PBKDF2)
- **Rate Limiting**: Prevent abuse and spam
- **Data Encryption**: At rest and in transit

### Performance
- **Database Optimization**: Indexed queries, efficient relationships
- **Caching**: Redis for session management
- **CDN**: Static asset delivery
- **Monitoring**: Application performance monitoring

### Scalability
- **Modular Architecture**: Easy to remove subscription features
- **Self-Hosting Support**: Separate version without payment code
- **API Design**: RESTful API for future integrations
- **Database Migrations**: Alembic for schema changes

## User Experience

### Onboarding
- **Documentation**: Comprehensive guides with screenshots
- **Embedded Videos**: Tutorial videos within the application
- **Interactive Help**: Contextual help tooltips
- **Feature Tours**: Guided tours for new users

### Support System
- **Free Tier**: Community support (documentation, forums)
- **Paid Tiers**: Email support
- **Enterprise**: Priority support, direct contact
- **Self-Hosted**: Community support only

### Data Management
- **Export**: JSON export for all user data
- **Import**: Bulk import capabilities
- **Backup**: Automatic data backups
- **Migration**: Easy data migration between tiers

## Business Model

### Revenue Streams
- **Subscription Fees**: Monthly/annual payments
- **Enterprise Services**: Custom development, consulting
- **Self-Hosting**: Open source, community-driven

### Pricing Strategy
- **Freemium Model**: Free trial to paid conversion
- **Annual Discounts**: 2 months free for annual plans
- **Enterprise Pricing**: Custom pricing for large guilds
- **Grandfathering**: Existing users get free tier

### Marketing
- **Word of Mouth**: Guild leader referrals
- **Content Marketing**: Blog posts, tutorials
- **Community Building**: Discord server, forums
- **Partnerships**: Discord bot integrations

## Implementation Phases

### Phase 1: Core Migration (Weeks 1-4)
- Database schema updates
- Permission system implementation
- API endpoint migration
- Testing and validation

### Phase 2: Subscription System (Weeks 5-8)
- Stripe integration
- Subscription management
- Payment processing
- Billing dashboard

### Phase 3: Advanced Features (Weeks 9-12)
- Discord integration
- Advanced analytics
- Custom reports
- Enterprise features

### Phase 4: Polish & Launch (Weeks 13-16)
- Documentation
- Onboarding flows
- Performance optimization
- Production deployment

## Success Metrics

### Technical Metrics
- **Uptime**: 99.9% availability
- **Response Time**: <200ms API responses
- **Error Rate**: <0.1% error rate
- **Security**: Zero security incidents

### Business Metrics
- **Conversion Rate**: Trial to paid conversion
- **Churn Rate**: Monthly subscription retention
- **Revenue Growth**: Monthly recurring revenue
- **User Satisfaction**: Net Promoter Score

### User Metrics
- **Active Users**: Daily/monthly active users
- **Feature Adoption**: Usage of key features
- **Support Tickets**: Support request volume
- **User Feedback**: Feature request frequency

This specification provides a comprehensive foundation for building GuildRoster as a successful SaaS application for World of Warcraft guild management. 