# Technical Notes: Attendance Tracker Frontend

## Recommended Technology Stack

### 1. React Setup

**Recommendation: Vite**

**Reasons:**
- Faster development server and build times compared to Create React App
- Better optimized production builds
- Native ES modules support
- Smaller footprint for static deployments
- Built-in support for modern JavaScript features
- Excellent GitHub Pages deployment compatibility

**Setup Command:**
```bash
npm create vite@latest attendance-tracker -- --template react
```

**Alternatives Considered:**
- Create React App: More boilerplate, slower, being deprecated
- Next.js: Overkill for static-only site, adds unnecessary complexity

### 2. Chart Library

**Recommendation: Recharts**

**Reasons:**
- Built specifically for React (uses React components)
- Clean, declarative API
- Good documentation and examples
- Responsive by default
- Customizable bar charts perfect for monthly attendance percentages
- Smaller bundle size than Chart.js with React wrapper
- Active maintenance

**Installation:**
```bash
npm install recharts
```

**Example Usage:**
```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

<BarChart data={monthlyData}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="month" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="percentage" fill="#ef4444" />
</BarChart>
```

**Alternatives Considered:**
- Chart.js with react-chartjs-2: More setup, less React-native
- Victory: Larger bundle size
- Nivo: Overkill for simple bar charts

### 3. Calendar Component

**Recommendation: react-calendar**

**Reasons:**
- Lightweight and focused specifically on calendar UI
- Highly customizable for marking attended days
- Built-in navigation (previous/next month)
- Easy to style with Tailwind CSS
- Good mobile touch support
- Active maintenance

**Installation:**
```bash
npm install react-calendar
```

**Example Usage:**
```jsx
import Calendar from 'react-calendar';

<Calendar
  value={selectedDate}
  tileClassName={({ date }) => {
    return attendedDates.includes(date) ? 'attended-day' : null;
  }}
  onClickDay={(date) => showAttendanceDetails(date)}
/>
```

**Alternatives Considered:**
- react-big-calendar: Too complex for this use case
- Custom calendar component: Unnecessary development time
- FullCalendar: Overkill with event management features

### 4. Date Picker Component

**Recommendation: react-datepicker**

**Reasons:**
- Simple, lightweight date picker
- Easy integration with React state
- Good keyboard navigation
- Works well with Tailwind CSS styling
- Supports date range selection
- Mobile-friendly

**Installation:**
```bash
npm install react-datepicker
```

**Example Usage:**
```jsx
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

<DatePicker
  selected={startDate}
  onChange={(date) => setStartDate(date)}
  selectsStart
  startDate={startDate}
  endDate={endDate}
/>
```

**Alternatives Considered:**
- HTML5 native date input: Poor mobile UX, inconsistent browser support
- MUI DatePicker: Requires full Material-UI, too heavy
- react-day-picker: More complex API for this use case

## GitHub Pages Deployment

### Configuration Steps for Existing Repository

**1. Install GitHub Pages deployment package:**
```bash
npm install --save-dev gh-pages
```

**2. Update package.json:**
```json
{
  "name": "attendance-tracker",
  "homepage": "https://koustubh25.github.io/station-station",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  }
}
```

**3. Configure Vite for GitHub Pages:**

Create/update `vite.config.js`:
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/station-station/', // Important for existing repo deployment
  build: {
    outDir: 'dist',
  },
});
```

**4. Deployment Commands:**
```bash
# Build and deploy to GitHub Pages
npm run deploy
```

**5. Repository Settings:**
- Go to repository Settings > Pages
- Source: Deploy from branch
- Branch: gh-pages (auto-created by gh-pages package)
- Folder: / (root)

**6. Access URL:**
```
https://koustubh25.github.io/station-station/
```

### Important Notes for Existing Repo:
- The app will be deployed to the `gh-pages` branch
- Existing main branch code remains untouched
- The build output goes to `dist/` folder (configurable)
- Add `dist/` to `.gitignore` to avoid committing build files to main branch

## Fetching JSON from raw.githubusercontent.com

### CORS Considerations

**Good News:** GitHub's raw content URL supports CORS and allows cross-origin requests by default.

**Fetch Implementation:**

```javascript
const ATTENDANCE_JSON_URL = 'https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json';

async function fetchAttendanceData() {
  try {
    const response = await fetch(ATTENDANCE_JSON_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      cache: 'no-cache', // Ensure fresh data on reload
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to fetch attendance data:', error);
    throw error;
  }
}
```

### Best Practices:

**1. Error Handling:**
- Handle network failures gracefully
- Show user-friendly error messages
- Provide retry mechanism if needed

**2. Loading States:**
```jsx
const [attendanceData, setAttendanceData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  fetchAttendanceData()
    .then(data => {
      setAttendanceData(data);
      setLoading(false);
    })
    .catch(err => {
      setError(err.message);
      setLoading(false);
    });
}, []);
```

**3. Cache Considerations:**
- raw.githubusercontent.com has caching headers
- Using `cache: 'no-cache'` ensures fresh data on page reload
- Consider showing last update timestamp to user

**4. Data Validation:**
- Validate JSON structure before using
- Handle missing or malformed data gracefully
- Type checking for expected fields

### Testing Locally:

**Development Mode:**
- No CORS issues when fetching from raw.githubusercontent.com
- Works identically in development and production

**Mock Data for Development (Optional):**
```javascript
const DEV_MODE = import.meta.env.DEV;
const ATTENDANCE_JSON_URL = DEV_MODE
  ? '/mock-data/attendance.json' // Local fallback
  : 'https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json';
```

## Project Structure Recommendation

```
attendance-tracker/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── UserSelector.jsx
│   │   ├── CalendarView.jsx
│   │   ├── AttendanceChart.jsx
│   │   ├── DateRangeFilter.jsx
│   │   ├── SummaryStats.jsx
│   │   └── AttendanceDetails.jsx (modal/tooltip)
│   ├── hooks/
│   │   ├── useAttendanceData.js
│   │   └── useFilteredData.js
│   ├── utils/
│   │   ├── dataFetcher.js
│   │   ├── dateHelpers.js
│   │   └── calculations.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css (Tailwind imports)
├── .gitignore
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

## CSS Framework Setup: Tailwind CSS

**Installation:**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Configure tailwind.config.js:**
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'attended': '#ef4444', // Red for attended days
      },
    },
  },
  plugins: [],
}
```

**Add to src/index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Additional Recommendations

### State Management:
- **No external state library needed** - React useState and useContext sufficient
- Use React Context only if prop drilling becomes excessive
- Keep state close to where it's used

### Performance Optimizations:
- Use React.memo for expensive components (calendar tiles)
- Debounce date range filter changes
- Lazy load chart library if needed
- Use useMemo for filtered/calculated data

### Accessibility:
- Ensure calendar is keyboard navigable
- Provide ARIA labels for interactive elements
- Ensure color contrast meets WCAG standards
- Support screen readers for statistics

### Mobile Considerations:
- Touch-friendly date pickers (large tap targets)
- Responsive chart sizing
- Swipe gestures for month navigation (if using react-calendar)
- Optimize for smaller screens with vertical layout

## Environment Variables (Optional)

Create `.env` file for configuration:
```
VITE_ATTENDANCE_JSON_URL=https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json
VITE_DEFAULT_START_DATE=2025-10-01
```

Access in code:
```javascript
const JSON_URL = import.meta.env.VITE_ATTENDANCE_JSON_URL;
```

## Testing Recommendations

**Unit Testing:**
- Vitest (built-in with Vite)
- React Testing Library
- Test utility functions (date calculations, filtering)

**E2E Testing (Optional):**
- Playwright or Cypress
- Test critical user flows
- Visual regression testing

**Manual Testing Checklist:**
- Mobile responsiveness (iPhone, Android)
- Different screen sizes (tablet, desktop)
- Browser compatibility (Chrome, Safari, Firefox)
- Data loading states and errors
- Date filtering edge cases
