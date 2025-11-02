# Product Mission

## Pitch
Station Station is a personal attendance tracking application that helps Melbourne train commuters monitor their office attendance by analyzing Myki metro transaction data. It provides transparency into actual work-from-office compliance, helping users plan their schedules to meet company-mandated attendance requirements without manual tracking.

## Users

### Primary Customers
- **Melbourne train commuters**: Professionals who use Melbourne's metro system to commute to work and need to track their office attendance
- **Hybrid workers with attendance requirements**: Employees whose companies mandate specific office attendance percentages (e.g., 50% work-from-office policies)

### User Personas

**Suburban Commuter** (25-45 years)
- **Role:** Full-time professional working in Melbourne CBD
- **Context:** Lives outside the city center and relies on trains for daily commute. Works under a hybrid policy requiring 50% office attendance but lacks visibility into current compliance.
- **Pain Points:**
  - No way to know actual attendance percentage without manual counting
  - Risk of non-compliance with company attendance policies
  - Difficulty planning upcoming work weeks without knowing current status
  - Lack of transparency from employer systems
- **Goals:**
  - Accurately track office attendance based on actual commute data
  - Plan future weeks to meet attendance requirements
  - Avoid manual record-keeping and guesswork

## The Problem

### Lack of Attendance Transparency
Many companies now enforce hybrid work policies with specific office attendance requirements (commonly 50% or more), yet they provide no tools or transparency for employees to track their current compliance status. This creates anxiety and planning difficulties for workers who want to meet requirements but have no reliable way to measure their actual attendance percentage.

**Impact:** Employees must either manually track every office visit (error-prone and time-consuming) or risk falling short of requirements and facing consequences.

**Our Solution:** Station Station automatically determines office attendance by analyzing Myki transaction history. If a user tapped on/off at their designated work station on any given day, it counts as office attendance. The app presents this data with monthly statistics, giving users complete visibility into their compliance status.

## Differentiators

### Automated Truth from Transit Data
Unlike manual tracking spreadsheets or company-provided systems that may be inaccurate or delayed, Station Station uses actual Myki transaction records as the source of truth. This eliminates human error and provides an objective, verifiable attendance record based on real commute data.

This results in accurate, trustworthy attendance tracking that requires zero manual input once configured.

### Privacy and Personal Control
Unlike employer-controlled attendance systems, Station Station gives users personal ownership of their data. Attendance records are stored locally in JSON format and can optionally be version-controlled in a personal GitHub repository. Users maintain complete control over their credentials and data.

This results in peace of mind about data privacy while still providing the transparency needed for compliance planning.

## Key Features

### Core Features
- **Automated Myki Data Extraction:** Securely logs into Myki account via headless browser, selects specified card, and extracts transaction history for a user-defined date range.
- **Station-Based Attendance Detection:** Analyzes transaction data to determine if user visited designated work station on each day, creating a binary attendance record.
- **Monthly Summary Statistics:** Calculates and displays attendance percentages for each month, providing clear visibility into compliance with company requirements.

### Data Management Features
- **JSON File Storage:** Maintains attendance records in a structured JSON format for portability and easy data access.
- **GitHub Integration:** Supports pushing attendance data to a GitHub repository for version control and historical tracking.

### User Configuration Features
- **Flexible Setup:** Allows users to configure Myki credentials, card number, designated work station name, and date range for analysis.
- **Visual Dashboard:** Provides a React-based UI to view attendance on specific days and browse monthly statistics at a glance.
