# Tech Stack

## Framework & Runtime
- **Backend Language:** Python 3.x
- **Backend Environment:** Local virtual environment (venv)
- **Frontend Framework:** React
- **Package Manager (Backend):** pip
- **Package Manager (Frontend):** npm or yarn

## Frontend
- **JavaScript Framework:** React
- **CSS Framework:** TBD (Tailwind CSS, Bootstrap, or custom)
- **UI Components:** Custom components for calendar view and statistics dashboard

## Browser Automation & Web Scraping
- **Headless Browser:** Playwright or Puppeteer (Node.js-based) or Selenium (Python-based)
- **Anti-Bot Bypass:** Techniques and libraries for bypassing Cloudflare bot detection
  - Potential tools: undetected-chromedriver, playwright-stealth, or custom browser fingerprinting
- **HTTP Client:** Python requests library (for direct API calls after authentication)

## Data Storage
- **Primary Storage:** JSON files (local filesystem)
- **Data Structure:** Structured JSON with daily attendance records and monthly aggregations
- **Version Control:** Git-based storage with GitHub repository integration (optional)

## Authentication & Security
- **Credential Storage:** Environment variables or encrypted local configuration file
- **Session Management:** Cookie and header extraction from authenticated browser session
- **Secrets Management:** .env file for local development (never committed to version control)

## Testing & Quality
- **Backend Testing:** pytest
- **Frontend Testing:** Jest and React Testing Library
- **Linting (Backend):** pylint or flake8
- **Linting (Frontend):** ESLint
- **Code Formatting:** Prettier (frontend), black (backend)

## Development & Infrastructure
- **Version Control:** Git
- **Repository Hosting:** GitHub (also used for optional data backup)
- **Local Development:** Python venv for backend, Node.js for frontend development server
- **Environment Management:** .env files for configuration

## Third-Party Services
- **External API:** Myki portal (ptv.vic.gov.au or mymyki.com.au)
- **GitHub API:** For optional automated commits and pushing of attendance data

## Key Technical Challenges
- **Cloudflare Bot Detection:** Primary technical challenge requiring sophisticated browser automation techniques, proper user-agent and header configuration, and potentially browser fingerprinting evasion
- **Session Persistence:** Maintaining authenticated session across multiple API calls
- **API Discovery:** Reverse engineering undocumented Myki API endpoints through network traffic analysis
