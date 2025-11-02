/**
 * Date helper utilities for attendance data processing
 */

/**
 * Parse attendance date string (YYYY-MM-DD) to Date object
 * @param {string} dateString - Date string in YYYY-MM-DD format
 * @returns {Date} Parsed Date object
 */
export function parseAttendanceDate(dateString) {
  const date = new Date(dateString);
  // Ensure the date is valid
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid date string: ${dateString}`);
  }
  return date;
}

/**
 * Check if a date falls within a specified range (inclusive)
 * @param {Date} date - The date to check
 * @param {Date} startDate - Start of the range
 * @param {Date} endDate - End of the range
 * @returns {boolean} True if date is within range
 */
export function isDateInRange(date, startDate, endDate) {
  const dateTime = date.getTime();
  const startTime = startDate.getTime();
  const endTime = endDate.getTime();

  return dateTime >= startTime && dateTime <= endTime;
}

/**
 * Format a date range for display
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @returns {string} Formatted date range (e.g., "Oct 01, 2025 - Nov 02, 2025")
 */
export function formatDateRange(startDate, endDate) {
  const options = { year: 'numeric', month: 'short', day: '2-digit' };
  const start = startDate.toLocaleDateString('en-US', options);
  const end = endDate.toLocaleDateString('en-US', options);

  return `${start} - ${end}`;
}

/**
 * Convert month string (YYYY-MM) to readable label
 * @param {string} monthString - Month in YYYY-MM format (e.g., "2025-05")
 * @returns {string} Formatted month label (e.g., "May 2025")
 */
export function getMonthLabel(monthString) {
  const [year, month] = monthString.split('-');
  const date = new Date(year, parseInt(month) - 1, 1);

  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
}
