/**
 * Application configuration constants
 */

/**
 * URL for fetching attendance data from GitHub
 */
export const ATTENDANCE_JSON_URL =
  'https://raw.githubusercontent.com/koustubh25/station-station/main/output/attendance.json';

/**
 * Default start date for filtering (Financial year start: October 1, 2025)
 */
export const DEFAULT_START_DATE = new Date('2025-10-01');

/**
 * Default end date for filtering (current date)
 */
export const DEFAULT_END_DATE = new Date();

/**
 * Color used for marking attended days (red theme)
 */
export const ATTENDED_DAY_COLOR = '#ef4444';

/**
 * Color used for marking manual attendance days (amber/orange theme)
 */
export const MANUAL_ATTENDANCE_COLOR = '#f59e0b';

/**
 * Attendance color map for different attendance types
 */
export const ATTENDANCE_COLORS = {
  ptv: '#ef4444',      // Red for PTV-detected attendance
  manual: '#f59e0b',   // Amber/orange for manual attendance
};
