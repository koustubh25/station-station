# Code Highlights - Task Group 6 Implementation

## Key Implementation Details

### 1. App.jsx - Main Application Component

#### State Management
```javascript
// Core application state
const [selectedUser, setSelectedUser] = useState('');
const [startDate, setStartDate] = useState(DEFAULT_START_DATE);
const [endDate, setEndDate] = useState(DEFAULT_END_DATE);
const [selectedAttendanceDay, setSelectedAttendanceDay] = useState(null);
const [selectedMonth, setSelectedMonth] = useState(new Date());
```

#### Data Fetching with Custom Hook
```javascript
// Fetch attendance data from GitHub
const { data, loading, error, refetch } = useAttendanceData();

// Get list of users (exclude metadata)
const users = useMemo(() => {
  if (!data) return [];
  return Object.keys(data).filter(key => key !== 'metadata');
}, [data]);

// Auto-select first user on load
useEffect(() => {
  if (users.length > 0 && !selectedUser) {
    setSelectedUser(users[0]);
  }
}, [users, selectedUser]);
```

#### Data Filtering with Performance Optimization
```javascript
// Get filtered data for selected user and date range
const { filteredMonthlyData, summaryStats, attendedDates } = useFilteredData(
  data,
  selectedUser,
  startDate,
  endDate
);

// Memoized date range formatting
const dateRangeText = useMemo(() => {
  return formatDateRange(startDate, endDate);
}, [startDate, endDate]);
```

#### Event Handlers
```javascript
// User selection change
const handleUserChange = (username) => {
  setSelectedUser(username);
  setSelectedAttendanceDay(null); // Clear modal
};

// Date range changes
const handleStartDateChange = (date) => setStartDate(date);
const handleEndDateChange = (date) => setEndDate(date);

// Calendar month navigation
const handleMonthChange = (newMonth) => setSelectedMonth(newMonth);

// Attended day click - open modal
const handleDayClick = (dateString) => {
  if (!data || !selectedUser) return;

  const userData = data[selectedUser];
  if (!userData || !userData.attendanceDays) return;

  const attendanceRecord = userData.attendanceDays.find(
    (record) => record.date === dateString
  );

  if (attendanceRecord) {
    setSelectedAttendanceDay({
      date: dateString,
      timestamp: attendanceRecord.timestamp,
      station: attendanceRecord.targetStation || userData.targetStation || 'Unknown'
    });
  }
};

// Close modal
const handleCloseModal = () => setSelectedAttendanceDay(null);
```

#### Last Updated Metadata Display
```javascript
// Extract and format last updated timestamp
const lastUpdated = useMemo(() => {
  if (!data || !data.metadata || !data.metadata.lastUpdated) {
    return null;
  }
  const date = new Date(data.metadata.lastUpdated);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}, [data]);
```

### 2. Responsive Layout Structure

#### Mobile-First Container
```javascript
<div className="min-h-screen bg-gray-50">
  <main className="container mx-auto px-4 py-6 sm:px-6 lg:px-8">
    {/* Content */}
  </main>
</div>
```

#### Responsive Header
```javascript
<header className="mb-6 sm:mb-8">
  <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
    Attendance Tracker
  </h1>
  {lastUpdated && (
    <p className="text-sm text-gray-600">
      Last updated: {lastUpdated}
    </p>
  )}
</header>
```

#### Responsive Grid for Visualizations
```javascript
<section
  className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6"
  aria-label="Attendance visualizations"
>
  {/* Calendar view */}
  <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 border border-gray-200">
    <CalendarView {...props} />
  </div>

  {/* Attendance chart */}
  <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 border border-gray-200">
    <AttendanceChart {...props} />
  </div>
</section>
```

### 3. Accessibility Implementation

#### Semantic Sections with ARIA Labels
```javascript
<section className="mb-6" aria-label="User selection">
  <UserSelector {...props} />
</section>

<section className="mb-6" aria-label="Date range filter">
  <DateRangeFilter {...props} />
</section>

<section className="mb-6" aria-label="Attendance summary">
  <SummaryStats {...props} />
</section>
```

#### Loading State with Screen Reader Support
```javascript
if (loading) {
  return (
    <div className="min-h-screen bg-gray-50">
      <LoadingSpinner />
    </div>
  );
}
```

LoadingSpinner component:
```javascript
<div
  className="flex flex-col items-center justify-center min-h-[400px]"
  role="status"
  aria-live="polite"
>
  <div className="w-16 h-16 border-4 border-gray-200 border-t-attended rounded-full animate-spin" />
  <p className="mt-4 text-lg text-gray-600 font-medium">
    Loading attendance data...
  </p>
</div>
```

#### Error State with Retry
```javascript
if (error) {
  return (
    <div className="min-h-screen bg-gray-50">
      <ErrorMessage message={error} onRetry={refetch} />
    </div>
  );
}
```

### 4. Conditional Modal Rendering

```javascript
{/* Attendance details modal (conditional) */}
{selectedAttendanceDay && (
  <AttendanceDetails
    date={selectedAttendanceDay.date}
    timestamp={selectedAttendanceDay.timestamp}
    station={selectedAttendanceDay.station}
    onClose={handleCloseModal}
  />
)}
```

### 5. Component Prop Passing

#### UserSelector
```javascript
<UserSelector
  users={users}
  selectedUser={selectedUser}
  onUserChange={handleUserChange}
/>
```

#### DateRangeFilter
```javascript
<DateRangeFilter
  startDate={startDate}
  endDate={endDate}
  onStartDateChange={handleStartDateChange}
  onEndDateChange={handleEndDateChange}
/>
```

#### SummaryStats
```javascript
<SummaryStats
  statistics={summaryStats}
  dateRange={dateRangeText}
/>
```

#### CalendarView
```javascript
<CalendarView
  attendedDates={attendedDates}
  selectedMonth={selectedMonth}
  onMonthChange={handleMonthChange}
  onDayClick={handleDayClick}
  dateRange={{ start: startDate, end: endDate }}
/>
```

#### AttendanceChart
```javascript
<AttendanceChart
  monthlyData={filteredMonthlyData}
  dateRange={{ start: startDate, end: endDate }}
/>
```

### 6. HTML Metadata (index.html)

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta
      name="description"
      content="Track and visualize work attendance data with interactive calendar views, monthly statistics, and detailed analytics. Built with React and Tailwind CSS."
    />
    <title>Attendance Tracker</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### 7. CSS Imports (main.jsx)

```javascript
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
// Import required CSS for external libraries
import 'react-calendar/dist/Calendar.css';
import 'react-datepicker/dist/react-datepicker.css';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

---

## Responsive Breakpoints Usage

### Mobile (Default, < 640px)
- `className="px-4 py-6"` - Base padding
- `className="text-3xl"` - Base heading size
- `className="grid grid-cols-1"` - Single column layout

### Tablet (sm: 640px+)
- `className="sm:px-6"` - Increased padding
- `className="sm:text-4xl"` - Larger heading
- `className="sm:grid-cols-2"` - Two-column grid
- `className="sm:p-6"` - Larger card padding

### Desktop (lg: 1024px+)
- `className="lg:px-8"` - Maximum padding
- `className="lg:grid-cols-2"` - Side-by-side visualizations

---

## Accessibility Features Implemented

### 1. Semantic HTML
- `<main>` for primary content
- `<header>` for page heading
- `<section>` for logical grouping
- `<footer>` for credits

### 2. ARIA Attributes
- `aria-label` on sections
- `role="status"` on loading
- `role="alert"` on errors
- `aria-live` for dynamic content
- `aria-modal` on modal

### 3. Keyboard Navigation
- All interactive elements focusable
- Visible focus rings
- Logical tab order
- Modal focus trap

### 4. Screen Reader Support
- Descriptive labels
- Live region announcements
- Proper heading hierarchy

---

## Performance Optimizations

### 1. Memoization
```javascript
const users = useMemo(() => { /* ... */ }, [data]);
const dateRangeText = useMemo(() => { /* ... */ }, [startDate, endDate]);
const lastUpdated = useMemo(() => { /* ... */ }, [data]);
```

### 2. Custom Hook Memoization
```javascript
// useFilteredData hook uses useMemo internally
const { filteredMonthlyData, summaryStats, attendedDates } = useFilteredData(
  data,
  selectedUser,
  startDate,
  endDate
);
```

### 3. Conditional Rendering
```javascript
// Early return for loading state
if (loading) return <LoadingSpinner />;

// Early return for error state
if (error) return <ErrorMessage />;

// Only render modal when needed
{selectedAttendanceDay && <AttendanceDetails />}
```

---

## Error Handling

### 1. Data Fetch Errors
```javascript
if (error) {
  return (
    <div className="min-h-screen bg-gray-50">
      <ErrorMessage message={error} onRetry={refetch} />
    </div>
  );
}
```

### 2. No Data State
```javascript
if (!data || users.length === 0) {
  return (
    <div className="min-h-screen bg-gray-50">
      <ErrorMessage
        message="No attendance data available. Please check the data source."
        onRetry={refetch}
      />
    </div>
  );
}
```

### 3. Safe Data Access
```javascript
const userData = data[selectedUser];
if (!userData || !userData.attendanceDays) return;
```

---

## File Sizes

- **App.jsx:** 254 lines
- **main.jsx:** 13 lines
- **index.html:** 18 lines

Total Implementation: ~285 lines of code

---

## Build Metrics

```
Production Build:
- Total modules transformed: 1,185
- Build time: 5.16s
- HTML size: 0.72 kB (0.41 kB gzipped)
- CSS size: 41.92 kB (7.45 kB gzipped)
- JS size: 739.61 kB (216.29 kB gzipped)
```

---

## Browser DevTools Verification

### Console Output (Expected)
- No errors
- No warnings
- Successful data fetch from GitHub URL

### Network Tab (Expected)
- GET attendance.json: 200 OK
- react-calendar.css: 200 OK
- react-datepicker.css: 200 OK

### Accessibility Tab (Expected)
- No ARIA violations
- Proper heading hierarchy
- All interactive elements labeled

---

This implementation represents production-ready code with comprehensive error handling, accessibility features, responsive design, and performance optimizations.
