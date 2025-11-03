# Specification: Attendance Tracker Frontend UI

## Goal
Build a responsive static React web application to visualize work attendance data from the Myki attendance tracker JSON output, enabling users to view attendance statistics, explore monthly calendars with marked attended days, analyze trends through bar charts, and filter data by date ranges across mobile and desktop devices.

## User Stories
- As a user, I want to select my username from a dropdown so that I can view my personal attendance data
- As a user, I want to see a monthly calendar with my attended days visually marked so that I can quickly identify when I was at the office
- As a user, I want to view monthly attendance percentages in a bar chart so that I can understand my attendance trends over time
- As a user, I want to filter data by date range so that I can focus on specific time periods like quarters or financial years

## Specific Requirements

**Data Fetching and Loading**
- Fetch attendance data from GitHub raw URL: https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json
- Implement loading state with spinner or skeleton UI while data is being fetched
- Handle network errors with user-friendly error messages and retry option
- Use cache: 'no-cache' option to ensure fresh data on each page load
- Validate JSON structure and handle malformed data gracefully
- Display last updated timestamp from JSON metadata to inform users of data freshness
- No automatic refresh mechanism - data refreshes only on manual page reload

**User Selection Component**
- Render dropdown menu populated from JSON object keys (usernames)
- Always visible regardless of number of users in the dataset
- Pre-select first user by default on initial load
- Update all views (calendar, chart, statistics) when user selection changes
- Use semantic HTML select element for accessibility
- Style with Tailwind CSS for consistent appearance across devices

**Calendar View Component**
- Display monthly grid calendar showing current month by default
- Provide previous/next month navigation buttons for browsing history
- Mark attended days with red visual indicators (red background circle or dot)
- Make attended days clickable to show detail modal or tooltip
- Display timestamp and target station name when attended day is clicked
- Use react-calendar library for calendar functionality
- Ensure keyboard navigation support for accessibility
- Mobile-optimized with touch-friendly date selection
- Filter calendar display based on selected date range from date pickers

**Monthly Bar Chart Visualization**
- Display one bar per month showing attendance percentage (0-100%)
- Use Recharts library for rendering responsive bar charts
- Color bars in red theme to match attended day indicators
- Include tooltips showing exact percentage, working days, and days attended on hover
- Filter chart data based on selected date range from date pickers
- Ensure chart is fully responsive and readable on mobile screens
- Show clear axis labels (Month on X-axis, Percentage on Y-axis)
- Display only months that have data within the filtered date range

**Date Range Filtering Component**
- Provide two date picker inputs: start date and end date
- Default start date: October 1, 2025 (financial year start)
- Default end date: current date (present)
- Use react-datepicker library for date selection UI
- Apply filters to both calendar view and bar chart simultaneously
- Validate that end date is not before start date
- Persist date range selection in component state
- Provide clear labels and accessible form controls

**Summary Statistics Display**
- Show total attendance percentage for selected date range
- Display selected date range being viewed (formatted as "MMM DD, YYYY - MMM DD, YYYY")
- Show total working days count within the date range
- Display days attended count
- Show days missed count
- Calculate statistics dynamically based on filtered data
- Use clear, large typography for key metrics
- Organize statistics in a visually scannable card or panel layout

**Responsive Design Implementation**
- Use mobile-first development approach with progressive enhancement
- Implement standard Tailwind breakpoints (sm: 640px, md: 768px, lg: 1024px)
- Stack components vertically on mobile, arrange in grid on desktop
- Ensure minimum 44x44px tap targets for all interactive elements on mobile
- Optimize calendar and chart sizing for iPhone and Android devices
- Test across mobile, tablet, and desktop screen sizes
- Use relative units (rem/em) for scalable typography

**Technology Stack and Setup**
- Use Vite as build tool with React template for faster development and builds
- Configure Tailwind CSS for styling with custom color for attended days (#ef4444)
- Install and configure react-calendar for calendar grid functionality
- Install and configure Recharts for bar chart visualization
- Install and configure react-datepicker for date range selection
- Set up GitHub Pages deployment with gh-pages package
- Configure vite.config.js with base: '/station-station/' for existing repo deployment
- Create project structure with organized components, hooks, and utils folders

**Accessibility Requirements**
- Use semantic HTML elements (nav, main, button, select) throughout
- Ensure all interactive elements are keyboard accessible with visible focus states
- Provide ARIA labels for calendar navigation and chart elements
- Maintain color contrast ratio of at least 4.5:1 for text
- Include descriptive labels for all form inputs (user selector, date pickers)
- Support screen reader navigation for statistics and data display
- Use proper heading hierarchy (h1-h6) for document structure
- Manage focus appropriately when opening/closing attendance detail modals

**Error Handling and Validation**
- Show user-friendly error messages for network failures without technical details
- Provide retry button when data fetch fails
- Validate date range inputs and show clear error if end date precedes start date
- Handle missing or malformed JSON fields gracefully with fallback values
- Display informative message if no data exists for selected date range
- Log errors to console for debugging while showing clean UI to users

## Out of Scope
- Export features (CSV or PDF downloads)
- Comparison views between different months or users
- Continuous auto-refresh mechanism or polling
- Backend server or API development
- User authentication or login system
- Data editing or modification capabilities
- Multi-user comparison views showing multiple users simultaneously
- Email notifications or alerts
- Custom public holiday configuration for different regions
- Offline mode or service worker caching
- Dark mode or theme switching
