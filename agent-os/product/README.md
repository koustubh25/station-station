# Station Station - Product Documentation

**Product:** Station Station (Myki Attendance Tracker)
**Status:** ✅ Production Ready
**Live Application:** https://koustubh25.github.io/station-station/
**Repository:** https://github.com/koustubh25/station-station
**Last Updated:** November 2, 2025

## Overview

Station Station is a personal attendance tracking application that helps Melbourne train commuters monitor their office attendance by analyzing Myki metro transaction data. It provides transparency into actual work-from-office compliance through automated data extraction and an interactive web dashboard.

## Documentation Index

### 1. Product Strategy Documents

#### [Product Mission](./mission.md)
Complete product mission statement including:
- Product pitch and value proposition
- Target users and personas
- Problem statement and solution approach
- Key differentiators and features

**Read this first** to understand the product vision and user needs.

#### [Product Roadmap](./roadmap.md)
Development roadmap with 8 major features:
1. ✅ Myki Authentication & Cloudflare Bypass
2. ✅ Transaction History API Reverse Engineering
3. ✅ Myki SDK / Data Retrieval
4. ✅ Card Selection & Date Range Handling
5. ✅ Attendance Logic & JSON Storage
6. ✅ GitHub Integration for Data Backup
7. ✅ React Frontend Dashboard
8. ✅ Configuration Management & User Setup

**All roadmap items completed** as of November 2, 2025.

#### [Tech Stack](./tech-stack.md)
Technology decisions and rationale covering:
- Backend: Python, Playwright, browser automation
- Frontend: React, Vite, Tailwind CSS v4
- Infrastructure: Docker, GitHub Actions, GitHub Pages
- Development tools and libraries

### 2. Attendance Tracker Frontend Documentation

#### [Attendance Tracker Specification](./attendance-tracker-spec.md)
Comprehensive specification for the React frontend including:
- **Complete feature documentation** (8 task groups)
- Component architecture and data flow
- Technology stack and dependencies
- Bug fixes and enhancements (timezone, public holidays, skip dates)
- Deployment configuration
- Testing strategy
- Performance optimizations
- Browser compatibility
- Known limitations
- Future enhancement opportunities

**Read this** for complete technical details about the frontend implementation.

#### [Attendance Tracker Lessons Learned](./attendance-tracker-lessons-learned.md)
In-depth analysis of technical decisions and learning outcomes:
- **Development methodology** (task group approach)
- **Critical technical decisions** (timezone handling, CSS specificity, performance)
- **User feedback integration** (weekend styling, skip dates)
- **Architecture decisions** (component structure, state management)
- **Deployment and DevOps** (GitHub Pages, Vite)
- **Code quality and maintainability**
- **Recommendations for future projects**

**Read this** to understand why specific technical choices were made and what was learned.

#### [Attendance Tracker Implementation Summary](./attendance-tracker-implementation-summary.md)
High-level project summary including:
- Development timeline and task groups
- Technical stack overview
- Key features implemented
- Backend integration details
- Critical bug fixes
- Performance metrics
- Deployment configuration
- File inventory
- Success metrics

**Read this** for a quick overview of what was built and how it performs.

## System Architecture

### Backend (Python + Playwright)
```
Browser Automation
    ↓
Myki Portal Authentication
    ↓
Transaction Data Extraction
    ↓
Attendance Logic Processing
    ↓
JSON File Generation (attendance.json)
    ↓
GitHub Commit & Push
```

**Key Components:**
- `src/browser_manager.py` - Browser automation and Cloudflare bypass
- `src/myki_tracker.py` - Main orchestration
- `src/transaction_processor.py` - Transaction analysis
- `src/output_manager.py` - JSON generation and GitHub integration
- `src/holiday_checker.py` - Public holiday detection

### Frontend (React + Vite)
```
GitHub (attendance.json)
    ↓
useAttendanceData hook
    ↓
App.jsx (state management)
    ↓
useFilteredData hook
    ↓
Components (CalendarView, AttendanceChart, SummaryStats, etc.)
    ↓
User Interface
```

**Key Components:**
- 8 React components (UI)
- 3 custom hooks (data management)
- 3 utility modules (calculations, fetching, date helpers)
- Tailwind CSS v4 for styling

### Deployment
```
GitHub Actions (scheduled daily)
    ↓
Run backend in Docker container
    ↓
Generate attendance.json
    ↓
Commit to main branch
    ↓
Frontend fetches updated JSON
    ↓
Users see latest data
```

## Key Features

### Backend Features
1. **Automated Myki Login** - Headless browser with Cloudflare bypass
2. **Transaction Extraction** - Scrapes transaction history for date range
3. **Attendance Detection** - Identifies office days based on station visits
4. **Skip Dates Support** - Excludes vacation/sick days from calculations
5. **JSON Export** - Structured data format with metadata
6. **GitHub Integration** - Automatic commits via GitHub Actions

### Frontend Features
1. **Multi-User Support** - Dropdown to select between users
2. **Interactive Calendar** - Visual attendance tracking with color coding
3. **Monthly Statistics** - Bar chart showing attendance percentages
4. **Summary Dashboard** - Key metrics at a glance
5. **Date Range Filtering** - Custom date ranges with financial year defaults
6. **Public Holidays** - Victoria, Australia holidays marked automatically
7. **Responsive Design** - Mobile-first, optimized for iPhone
8. **Accessibility** - WCAG 2.1 AA compliant

## Color Coding System

The frontend uses a consistent color scheme:
- 🔴 **Red Circles** - Attended days (office visits)
- 🟡 **Amber Text** - Skip dates (vacation, sick leave)
- 🔴 **Red Text** - Weekends and public holidays
- ⚪ **White** - Regular non-attended days

## Technical Highlights

### Backend
- **Cloudflare Bypass:** Successfully bypasses bot detection
- **Browser Profile Persistence:** Maintains login state across runs
- **Docker Containerization:** Runs in headed Chrome with Xvfb
- **GitHub Actions:** Scheduled daily execution

### Frontend
- **Timezone Handling:** Uses local timezone to avoid date offset bugs
- **Performance:** Lighthouse score 95+, < 1 second load time
- **Bundle Size:** 65KB gzipped
- **Public Holidays:** Automatic detection using date-holidays library
- **Mobile-First:** Optimized for iPhone with 44px tap targets

## Critical Lessons Learned

### 1. Timezone Handling
**Problem:** Calendar dates were off by 1 day due to UTC conversion.

**Solution:** Use `toLocaleDateString('en-CA')` instead of `toISOString()` for local date formatting.

**Impact:** This pattern is now used throughout the codebase for consistent date handling.

### 2. User Feedback Integration
**Example:** Initially planned to remove red weekend text, but user feedback revealed it was a valued feature.

**Learning:** Ask users before removing features that seem redundant. User preferences trump developer assumptions.

### 3. Mobile-First Design
**Approach:** Started with mobile layout, progressively enhanced for desktop.

**Benefit:** Forced prioritization of essential features, resulting in a clean, focused UI that works everywhere.

### 4. Accessibility from Start
**Approach:** Built WCAG 2.1 AA compliance into Task Group 1, not retrofitted later.

**Benefit:** Avoided costly refactoring and achieved full accessibility without technical debt.

## Project Statistics

### Backend
- **Lines of Code:** ~3,000 (Python)
- **Files:** ~15 modules
- **Dependencies:** Playwright, python-dotenv, holidays
- **Docker Image:** ~1.5GB

### Frontend
- **Lines of Code:** ~2,300 (JavaScript/JSX)
- **Components:** 8 main components
- **Custom Hooks:** 3 hooks
- **Bundle Size:** 220KB (65KB gzipped)
- **Lighthouse Score:** 95+ Performance

### Documentation
- **Product Docs:** 6 documents, ~20,000 words
- **Code Comments:** JSDoc on all components
- **README Files:** Backend + Frontend

## Maintenance and Support

### Current Status
- ✅ **Production:** Live and actively used
- ✅ **Stable:** No known critical bugs
- ✅ **Maintained:** Regular dependency updates

### Monitoring
- **Backend:** GitHub Actions logs
- **Frontend:** GitHub Pages uptime (99.9% SLA)
- **Errors:** No automated error tracking (add Sentry if needed)
- **Analytics:** None (privacy-first approach)

### Update Frequency
- **Backend:** Runs daily via GitHub Actions
- **Frontend:** Updated on-demand via `npm run deploy`
- **Dependencies:** Review monthly for security patches

## Future Enhancements (Not in Current Scope)

### Potential Features
1. Multi-user comparison views
2. Export to CSV/PDF
3. Attendance goal tracking with notifications
4. Predictive analytics and trends
5. Dark mode toggle
6. PWA with offline support
7. Real-time API instead of static JSON

### Technical Improvements
1. TypeScript migration for type safety
2. E2E tests with Playwright
3. Performance monitoring and budgets
4. Error tracking (Sentry)
5. CI/CD pipeline for frontend
6. Automated accessibility testing

## Getting Started

### For Users
1. Visit https://koustubh25.github.io/station-station/
2. Select your name from the dropdown
3. View your attendance on the calendar
4. Check monthly statistics and summary metrics

### For Developers

#### Backend Setup
```bash
# Clone repository
git clone https://github.com/koustubh25/station-station.git
cd station-station

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Myki credentials

# Run locally
python src/myki_tracker.py
```

#### Frontend Setup
```bash
# Navigate to frontend
cd attendance-tracker

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Deploy to GitHub Pages
npm run deploy
```

## Documentation Maintenance

### Keeping Documentation Updated

When making changes to the product:

1. **Update Roadmap** - Mark features as completed, add new ones
2. **Update Spec** - Document new features, bug fixes, changes
3. **Update Lessons Learned** - Capture new technical decisions and insights
4. **Update Implementation Summary** - Keep statistics and metrics current
5. **Update README** - This file should always reflect current state

### Documentation Philosophy

- **Comprehensive:** Cover all aspects of the product
- **Honest:** Document failures and lessons, not just successes
- **Actionable:** Provide concrete recommendations and code examples
- **Maintained:** Update regularly, don't let it go stale
- **Accessible:** Write for future developers and stakeholders

## References

### External Links
- **Live Application:** https://koustubh25.github.io/station-station/
- **GitHub Repository:** https://github.com/koustubh25/station-station
- **Myki Portal:** https://www.mymyki.com.au

### Internal Documentation
- [Backend README](../../README.md)
- [Frontend README](../../attendance-tracker/README.md)
- [Docker Setup](../../DOCKER_README.md)
- [GitHub Actions](../../GITHUB_ACTIONS_DEPLOYMENT.md)

## Contact and Support

For issues, questions, or contributions:
- **GitHub Issues:** https://github.com/koustubh25/station-station/issues
- **Repository:** https://github.com/koustubh25/station-station

---

**Document Version:** 1.0
**Last Updated:** November 2, 2025
**Maintained By:** Project Team
**Purpose:** Central index for all Station Station product documentation
