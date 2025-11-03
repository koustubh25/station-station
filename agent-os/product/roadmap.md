# Product Roadmap

1. [x] Myki Authentication & Cloudflare Bypass - Successfully authenticate with Myki portal using headless browser automation, bypass Cloudflare bot detection, and extract required authentication headers and cookies for subsequent API calls. `L` ✅ **COMPLETED**

2. [x] Transaction History API Reverse Engineering - Analyze Myki portal network requests to identify and reverse engineer the API endpoints used for fetching transaction history, including request parameters, headers, and response format. `M` ✅ **COMPLETED**

3. [x] Myki SDK / Data Retrieval - **If API reverse engineering succeeds:** Build a clean Myki SDK/API client for fetching transaction data. **If API reverse engineering fails:** Fallback to browser-based scraping to retrieve transaction history. Parse response to extract station names, timestamps, and transaction types (tap on/off). `M` ✅ **COMPLETED** (Browser-based approach)

4. [x] Card Selection & Date Range Handling - Implement functionality to programmatically select a specific Myki card from user's account and configure date range parameters for transaction queries. `S` ✅ **COMPLETED**

5. [x] Attendance Logic & JSON Storage - Create attendance detection logic that analyzes transactions to determine if user visited designated station each day, then generate and save attendance records in structured JSON format with daily and monthly aggregations. Includes skip dates support. `M` ✅ **COMPLETED**

6. [x] GitHub Integration for Data Backup - Implement optional GitHub repository integration allowing users to automatically commit and push attendance JSON files for version control and historical tracking. `S` ✅ **COMPLETED** (GitHub Actions deployment)

7. [x] React Frontend Dashboard - Build React application with UI components to display daily attendance calendar view, monthly summary statistics, and attendance percentage calculations for each month. Includes skip dates visualization and Victoria public holidays. `M` ✅ **COMPLETED** (Live at https://koustubh25.github.io/station-station/)

8. [x] Configuration Management & User Setup - Create configuration interface (CLI or simple UI) for users to securely input and store Myki credentials, card number, designated work station name, and default date range preferences. `S` ✅ **COMPLETED** (Environment variables + config files)

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
> - Phase 1 (Authentication) is critical blocker due to Cloudflare challenges and must be solved first
> - Subsequent features build progressively: auth -> API discovery -> data extraction -> storage -> visualization
> - Feature #4 is conditional: Build SDK if APIs are discovered, fallback to scraping if not
> - Preferred path: API-based SDK approach for cleaner, more maintainable solution
> - GitHub integration is optional/nice-to-have and can be implemented after core functionality works
