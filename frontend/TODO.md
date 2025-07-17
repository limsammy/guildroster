# GuildRoster Frontend TODO

## 📊 **PROJECT STATUS OVERVIEW**

This document outlines the current state of the GuildRoster frontend implementation and tracks remaining work.

---

## ✅ **COMPLETED (Backend)**

### **Core Infrastructure**
- ✅ FastAPI backend with comprehensive API documentation
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Alembic migrations system
- ✅ Token-based authentication system
- ✅ User management with password hashing
- ✅ Comprehensive test suite

### **Database Models & API Endpoints**
- ✅ **Users** - Full CRUD with authentication
- ✅ **Tokens** - API authentication system
- ✅ **Guilds** - Full CRUD operations
- ✅ **Teams** - Full CRUD with guild relationships
- ✅ **Members** - Full CRUD with team assignments
- ✅ **Toons** - Full CRUD with class/role management
- ✅ **Raids** - Full CRUD with scheduling
- ✅ **Scenarios** - Full CRUD with active/inactive status
- ✅ **Attendance** - Comprehensive tracking with bulk operations, statistics, and reporting

### **Advanced Features**
- ✅ Bulk attendance operations (create/update)
- ✅ Attendance statistics and streak tracking
- ✅ Date range filtering and reporting
- ✅ Comprehensive API documentation (Swagger/ReDoc)

---

## ✅ **COMPLETED (Frontend)**

### **Core Infrastructure**
- ✅ React + TypeScript + Vite setup
- ✅ Tailwind CSS styling
- ✅ React Router for navigation
- ✅ Authentication context and protected routes
- ✅ API service layer with all endpoints

### **Pages & Components**
- ✅ **Login page** - Authentication with token management
- ✅ **Dashboard** - Overview with statistics and recent raids
- ✅ **Members page** - Full CRUD with search/filter
- ✅ **MemberForm component** - Add/edit member functionality
- ✅ **Guilds page** - Full CRUD with search and statistics
- ✅ **GuildForm component** - Add/edit guild functionality
- ✅ **UI Components** - Button, Card, Container, etc.

---

## ❌ **MISSING (Frontend)**

### **Core Management Pages**
- ✅ **Teams page** - List, create, edit, delete teams
- ✅ **Toons page** - List, create, edit, delete toons (with test fixes)
- ❌ **Raids page** - List, create, edit, delete raids
- ❌ **Scenarios page** - List, create, edit, delete scenarios

### **Attendance System**
- ❌ **Attendance page** - List, create, edit attendance records
- ❌ **Bulk attendance interface** - Bulk create/update operations
- ❌ **Attendance statistics pages** - Visual charts and analytics
- ❌ **Attendance reports** - Date range reports and exports

### **Advanced Features**
- ✅ **Guild Switching System** - Multi-guild management for superusers
- ❌ **User management** - User list, permissions (superuser only)
- ❌ **Token management** - API token management interface
- ❌ **Calendar view** - Raid scheduling calendar
- ❌ **Advanced filtering** - Complex search and filter interfaces
- ❌ **Export functionality** - CSV/PDF exports
- ❌ **Visual analytics** - Charts and graphs for attendance data

### **Navigation & Layout**
- ❌ **Sidebar navigation** - Main navigation menu
- ❌ **Breadcrumbs** - Navigation breadcrumbs
- ❌ **Responsive design** - Mobile-friendly layouts
- ❌ **Loading states** - Better loading indicators
- ❌ **Error boundaries** - Error handling components

---

## 📋 **IMPLEMENTATION PRIORITY**

### **Phase 1 Core Management (High Priority)**
1. ✅ **Guilds page** - Essential for guild management
   - ✅ Guilds list page with search/filter
   - ✅ GuildForm component for create/edit
   - ✅ Guild detail view
   - ✅ Delete confirmation
   - ✅ Tests for guild functionality
   - ✅ Removed faction field to match backend API

2. ✅ **Teams page** - Required for team organization
   - ✅ Teams list page (filtered by guild)
   - ✅ TeamForm component for create/edit
   - ✅ Team detail view with member list
   - ✅ Team assignment functionality
   - ✅ Tests for team functionality

3. ✅ **Toons page** - Character management
   - ✅ Toons list page (filtered by member)
   - ✅ ToonForm component with class/role selection
   - ✅ Toon detail view
   - ✅ Main/alt toon designation
   - ✅ Tests for toon functionality

4. ✅ **Member Detail Pages** - Enhanced member management
   - ✅ Individual member detail pages with toon list (/members/:id)
   - ✅ Create toons directly from member page (no member dropdown)
   - ✅ Member-specific toon management interface
   - ✅ Quick toon creation workflow
   - ✅ Member-toon relationship visualization
   - ✅ Enhanced toon creation flow with MemberSelector component
   - ✅ Fixed API type mismatch (display_name vs name)
   - ✅ Tests for member detail functionality

5. **Raids page** - Raid scheduling
   - [ ] Raids list page with date filtering
   - [ ] RaidForm component with scenario/difficulty selection
   - [ ] Raid detail view
   - [ ] Calendar view for raid scheduling
   - [ ] Team assignment for raids
   - [ ] Tests for raid functionality

6. **Scenarios page** - Raid instance management
   - [ ] Scenarios list page with active/inactive filter
   - [ ] ScenarioForm component for create/edit
   - [ ] Scenario detail view
   - [ ] Toggle scenario active status
   - [ ] Tests for scenario functionality

### **Phase 2: Attendance System (High Priority)**
1. **Attendance page** - Core attendance tracking
   - [ ] Attendance list page with advanced filtering
   - [ ] Create/edit attendance forms
   - [ ] Bulk attendance entry interface
   - [ ] Attendance detail view
   - [ ] Tests for attendance functionality

2. **Bulk attendance interface** - Efficient bulk operations
   - [ ] Bulk create attendance interface
   - [ ] Bulk update attendance interface
   - [ ] Import/export functionality
   - [ ] Batch operations with progress indicators
   - [ ] Tests for bulk operations

3. **Attendance statistics** - Analytics and reporting
   - [ ] Toon attendance statistics page
   - [ ] Member attendance statistics page
   - [ ] Team attendance statistics page
   - [ ] Raid attendance statistics page
   - [ ] Visual charts and graphs for attendance data
   - [ ] Tests for statistics functionality

### **Phase 3: Advanced Features (Medium Priority)**
1. ✅ **Guild Switching System** - Multi-guild management for superusers
   - ✅ GuildSwitcher component for superusers
   - ✅ GuildContext provider for app-wide guild state
   - ✅ Dashboard customization based on selected guild
   - ✅ Guild selection persistence (localStorage)
   - ✅ Hide guild-related UI for normal users
   - ✅ Tests for guild switching functionality

2. **Calendar view** - Visual raid scheduling
   - [ ] Monthly/weekly calendar view
   - [ ] Drag-and-drop raid scheduling
   - [ ] Calendar integration with raids
   - [ ] Tests for calendar functionality

3. **Advanced filtering** - Complex search capabilities
   - [ ] Multi-field search and filter
   - [ ] Date range filtering
   - [ ] Saved filter presets
   - [ ] Tests for filtering functionality

4. **Export functionality** - Data export features
   - [ ] CSV export for all data types
   - [ ] PDF reports generation
   - [ ] Attendance report exports
   - [ ] Tests for export functionality

5. **Visual analytics** - Charts and graphs
   - [ ] Attendance trend charts
   - [ ] Performance metrics visualization
   - [ ] Interactive dashboards
   - [ ] Tests for analytics functionality

### **Phase 4: Admin Features (Low Priority)**
1. **User management** - Superuser functionality
   - [ ] User list page (superuser only)
   - [ ] Create/edit user forms
   - [ ] User permissions management
   - [ ] Tests for user management

2. **Token management** - API token administration
   - [ ] Token list page
   - [ ] Create/edit token forms
   - [ ] Token expiration management
   - [ ] Tests for token management

### **Phase 5: Polish & UX (Ongoing)**
1. **Navigation & Layout**
   - [ ] Sidebar navigation menu
   - [ ] Breadcrumbs for navigation
   - [ ] Responsive design improvements
   - [ ] Mobile-friendly layouts

2. **User Experience**
   - [ ] Better loading states
   - [ ] Error boundaries and handling
   - [ ] Error notifications
   - [ ] Form validation improvements

3. **Performance**
   - [ ] Code splitting and lazy loading
   - [ ] Optimized API calls
   - [ ] Caching strategies
   - [ ] Bundle size optimization

---

## 🎯 **NEXT STEPS**

### **Immediate Priority**
1. ✅ **Implement Guilds page** - Foundation for guild management
2. ✅ **GuildForm component** - Reusable form for guild operations
3. ✅ **Create guild tests** - Ensure functionality works correctly
4. ✅ **Update navigation** - Add guilds to main navigation
5. ✅ **Implement Teams page** - Build on guilds foundation
6. ✅ **TeamForm component** - Reusable form for team operations

### **Short Term**
1. ✅ **Teams page** - Build on guilds foundation
2. ✅ **Toons page** - Character management (with test fixes)
3. ✅ **Member Detail Pages** - Enhanced member management and toon creation flow
4. **Raids page** - Raid scheduling and management
5. **Basic attendance page** - Core attendance tracking

### **Medium Term**
1. **Raids page** - Raid scheduling
2. **Scenarios page** - Raid instance management
3. **Bulk attendance interface** - Efficient operations

### **Long Term**
1. **Advanced analytics** - Charts and reporting
2. **Calendar view** - Visual scheduling
3. **Admin features** - User and token management

---

## 📝 **NOTES**

- All API endpoints are already implemented and tested
- Authentication system is complete and working
- UI components are reusable and well-structured
- Test infrastructure is in place for new features
- Focus on building features incrementally with proper testing
- Guild model simplified to match backend API (name field only)

---

## 🔄 **UPDATES**

- **2024-01-XX**: Created initial TODO document
- **2024-01-XX**: Completed Members page and form validation fixes
- **2024-01-XX**: All tests passing for existing functionality
- **2024-01-XX**: ✅ **COMPLETED** - Guilds page with full CRUD functionality
- **2024-01-XX**: ✅ **COMPLETED** - Removed faction field from Guild model to match backend API
- **2024-01-XX**: ✅ **COMPLETED** - Teams page with full CRUD functionality
- **2024-01-XX**: ✅ **COMPLETED** - Toons page with full CRUD functionality
- **2024-01-XX**: ✅ **COMPLETED** - Fixed test issues for multiple element matches and form submission
- **2024-01-XX**: ✅ **COMPLETED** - Member Detail Pages with enhanced toon creation flow 