# Spec Requirements: Attendance Tracker Frontend UI

## Initial Description
Build a frontend UI to visualize attendance data from output/attendance.json file. The UI should:

1. Allow user selection (username from JSON object keys)
2. Display a clickable calendar showing attended days with visual marks (circles, red color, etc.)
3. Show monthly attendance graphs with percentage and summary statistics from the JSON data

## Requirements Discussion

### First Round Questions

**Q1:** Should this be a standalone static React app that can be hosted on GitHub Pages, or does it need to integrate with an existing backend server?
**Answer:** Standalone static React app hosted on GitHub Pages.

**Q2:** For the data source, should the app fetch from the GitHub raw URL (https://raw.githubusercontent.com/username/repo/main/output/attendance.json), or will you have a local copy bundled with the deployment?
**Answer:** Fetch from GitHub raw URL: https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json

**Q3:** For the user selector, should it be a dropdown menu that's always visible, or should it be hidden if there's only one user in the JSON?
**Answer:** Dropdown menu that's always visible, even if there's only one user.

**Q4:** When clicking on an attended day in the calendar, what additional details should be shown? Just the timestamp and target station, or other fields too?
**Answer:** Show timestamp and target station.

**Q5:** For the monthly attendance graph, should it show one bar per day, or aggregate data differently (e.g., one bar per week, or per month over time)?
**Answer:** (See follow-up - Monthly attendance percentages, one bar per month)

**Q6:** Should there be any date range filtering options for the calendar and graph views, or should they always show all available data?
**Answer:** (See follow-up - Two date picker inputs for start/end date filtering)

**Q7:** What should be the default date range for viewing data? Should it default to showing the current month, last 30 days, or all available data?
**Answer:** (See follow-up - Default: October 1st, 2025 to present, which is the financial year)

**Q8:** For the summary statistics, which metrics should be displayed? Total attendance percentage, average per month, current streak, or others?
**Answer:** Total attendance percentage, date range, working days, days attended, and days missed.

**Q9:** Should the UI support responsive design for mobile devices, or is it primarily for desktop viewing?
**Answer:** Yes, responsive design for both mobile (iPhone) and desktop.

**Q10:** Do you have a preferred CSS framework or component library (e.g., Material-UI, Tailwind, Bootstrap), or should I suggest modern options?
**Answer:** Tailwind CSS or a similar neat framework.

**Q11:** For data refresh, should there be an auto-refresh mechanism, or just manual reload/refresh button?
**Answer:** Only automatic refresh on page load/reload. No auto-refresh mechanism needed.

**Q12:** Is there anything you specifically DON'T want in this feature that I should avoid including in the spec?
**Answer:** Exclude export features (CSV, PDF), comparison views between months.

### Follow-up Questions

**Follow-up 1:** For the date range filtering, would you prefer:
- Option A: Two date picker inputs (start date and end date) that filter the graph data
- Option B: Quick preset buttons (Last 7 days, Last 30 days, This Month, etc.) with optional custom range
- Option C: A combination of both presets and custom date pickers
**Answer:** Option A - Two date picker inputs (start date and end date) that filter the graph data.

**Follow-up 2:** For the calendar view, should it:
- Show the current month by default with navigation to view other months
- Show all months with attended days in a scrollable view
- Show the date range specified by the date pickers
**Answer:** Show the current month by default with navigation to view other months.

**Follow-up 3:** Since you mentioned GitHub Pages deployment, is this for:
- A new dedicated repository (so it will be at username.github.io/repo-name)
- The existing station-station repository (so it will be at username.github.io/station-station)
**Answer:** Existing station-station repository (so it will be at username.github.io/station-station).

**Follow-up 4:** For the bar chart showing monthly data, should each bar represent:
- The number of days attended in that month
- The attendance percentage for that month (attended days / working days * 100)
- Both metrics displayed together
**Answer:** Monthly attendance percentages (one bar per month).

### Existing Code to Reference

No similar existing features identified for reference.

## Visual Assets

### Files Provided:

No visual assets provided.

## Requirements Summary

### Functional Requirements

**Core Features:**
- Static React application with no backend server
- Hosted on GitHub Pages (existing station-station repository)
- Data fetching from: https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json
- Auto-refresh data only on page load/reload (no continuous auto-refresh)

**User Selection:**
- Dropdown menu for user selection
- Always visible, even with single user
- Populated from JSON object keys (usernames)

**Calendar View:**
- Monthly grid display showing current month by default
- Navigation arrows to browse previous/next months
- Attended days marked with visual indicators (red circles/dots)
- Clickable attended days showing detail popup/tooltip with:
  - Timestamp
  - Target station

**Bar Chart Visualization:**
- Display monthly attendance percentages
- One bar per month
- Filtered by date range selection

**Date Range Filtering:**
- Two date picker inputs (start date and end date)
- Default range: October 1st, 2025 to present (financial year start)
- Filters both calendar and graph views

**Summary Statistics Display:**
- Total attendance percentage
- Date range being viewed
- Total working days in range
- Days attended count
- Days missed count

**Design Requirements:**
- Responsive design for mobile (iPhone) and desktop viewports
- CSS framework: Tailwind CSS (or similar modern framework)
- Clean, neat visual presentation

### Reusability Opportunities

No similar existing features or components identified for reuse.

### Scope Boundaries

**In Scope:**
- Static React application
- GitHub Pages deployment on existing repository
- User selection dropdown
- Monthly calendar view with navigation
- Interactive attended day details
- Monthly attendance percentage bar chart
- Date range filtering (start/end date pickers)
- Summary statistics display
- Responsive mobile and desktop design
- Data fetching from GitHub raw URL
- Auto-refresh on page load only

**Out of Scope:**
- Export features (CSV, PDF downloads)
- Comparison views between months
- Continuous auto-refresh mechanism
- Backend server or API
- User authentication
- Data editing capabilities
- Multi-user comparison views

### Technical Considerations

**Data Source:**
- JSON fetched from GitHub raw URL
- CORS considerations for cross-origin requests
- Handle loading states and error scenarios

**Deployment:**
- GitHub Pages on existing station-station repository
- Static build output configuration
- Proper routing setup for SPA on GitHub Pages

**Technology Stack:**
- React framework (setup method TBD - Vite vs Create React App)
- Tailwind CSS for styling
- Chart library needed (recharts, chart.js, or similar)
- Calendar component library recommendation needed
- Date picker library recommendation needed

**Performance:**
- Efficient rendering for calendar views
- Optimized data filtering for large datasets
- Lazy loading or pagination if needed

**Browser Compatibility:**
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browser support (iOS Safari, Chrome Mobile)
