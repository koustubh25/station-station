# Attendance Tracker

A responsive React web application for visualizing and analyzing Myki attendance data. Track your station attendance patterns with interactive calendar views and monthly statistics.

## Live Demo

🔗 **[View Live Application](https://koustubh25.github.io/station-station/)**

## Features

- **User Selection**: Select from multiple users to view their attendance data
- **Interactive Calendar**: Monthly calendar view with attended days marked in red
- **Attendance Details**: Click on any attended day to view timestamp and station information
- **Monthly Bar Chart**: Visualize attendance percentages by month
- **Date Range Filtering**: Filter data using custom date ranges (default: Financial year starting Oct 1)
- **Summary Statistics**: View total attendance percentage, working days, days attended, and days missed
- **Responsive Design**: Optimized for mobile, tablet, and desktop devices
- **Accessible**: Full keyboard navigation, screen reader support, and WCAG 2.1 AA compliant

## Technology Stack

- **Frontend Framework**: React 18
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS v4
- **Charts**: Recharts
- **Calendar**: react-calendar
- **Date Picker**: react-datepicker
- **Testing**: Vitest + React Testing Library
- **Deployment**: GitHub Pages

## Data Source

The application fetches attendance data from:
```
https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json
```

Data is updated daily via automated GitHub Actions workflow.

## Local Development Setup

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Clone the repository:
```bash
git clone https://github.com/koustubh25/station-station.git
cd station-station/attendance-tracker
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173/station-station/`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run test` - Run tests
- `npm run test:ui` - Run tests with UI
- `npm run deploy` - Deploy to GitHub Pages

## Deployment

The application is configured to deploy to GitHub Pages using the `gh-pages` package.

To deploy:

```bash
npm run deploy
```

This will:
1. Build the production bundle
2. Push the `dist/` folder to the `gh-pages` branch
3. GitHub Pages will automatically serve the site

## Project Structure

```
attendance-tracker/
├── src/
│   ├── components/       # React components
│   │   ├── AttendanceChart.jsx
│   │   ├── AttendanceDetails.jsx
│   │   ├── CalendarView.jsx
│   │   ├── DateRangeFilter.jsx
│   │   ├── ErrorMessage.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── SummaryStats.jsx
│   │   └── UserSelector.jsx
│   ├── hooks/            # Custom React hooks
│   │   ├── useAttendanceData.js
│   │   └── useFilteredData.js
│   ├── utils/            # Utility functions
│   │   ├── calculations.js
│   │   ├── dataFetcher.js
│   │   └── dateHelpers.js
│   ├── constants/        # Configuration constants
│   │   └── config.js
│   ├── test/             # Test files
│   ├── App.jsx           # Main application component
│   ├── main.jsx          # Application entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── dist/                 # Production build (generated)
├── index.html            # HTML template
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
├── vitest.config.js      # Test configuration
└── package.json          # Dependencies and scripts
```

## Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest 2 versions)
- **Mobile Browsers**: iOS Safari 14+, Chrome Mobile, Firefox Mobile
- **Accessibility**: Screen readers (NVDA, JAWS, VoiceOver)

## Testing

The project includes comprehensive tests covering:
- Data layer (fetching, calculations, date helpers)
- UI components (user selector, calendar, charts, filters)
- Integration tests (complete user workflows)

Run tests:
```bash
npm run test
```

View test coverage:
```bash
npm run test -- --coverage
```

## Accessibility Features

- Semantic HTML throughout
- Full keyboard navigation support
- ARIA labels and roles
- Focus management for modals
- 4.5:1 color contrast ratio (WCAG AA)
- Screen reader announcements for dynamic content
- Minimum 44x44px tap targets on mobile

## License

This project is part of the station-station repository.

## Contributing

This is a personal attendance tracking project. For issues or questions, please open an issue in the main repository.
