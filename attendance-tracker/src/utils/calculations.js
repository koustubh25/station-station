import { parseAttendanceDate, isDateInRange, getMonthLabel } from './dateHelpers';

/**
 * Filter user attendance data by date range
 * @param {Object} userData - User attendance data object
 * @param {Date} startDate - Start date for filtering
 * @param {Date} endDate - End date for filtering
 * @returns {Object} Filtered data with attendedDates and monthlyBreakdown
 */
export function filterDataByDateRange(userData, startDate, endDate) {
  if (!userData || !userData.attendanceDays) {
    return {
      attendedDates: [],
      monthlyBreakdown: []
    };
  }

  // Filter attended days within date range
  const attendedDates = userData.attendanceDays
    .map(dateString => parseAttendanceDate(dateString))
    .filter(date => isDateInRange(date, startDate, endDate))
    .map(date => date.toISOString().split('T')[0]); // Convert back to YYYY-MM-DD

  // Filter monthly breakdown within date range
  const monthlyBreakdown = userData.statistics?.monthlyBreakdown?.filter(month => {
    const monthDate = parseAttendanceDate(`${month.month}-01`);
    return isDateInRange(monthDate, startDate, endDate);
  }) || [];

  return {
    attendedDates,
    monthlyBreakdown
  };
}

/**
 * Calculate summary statistics for filtered data
 * @param {Object} userData - User attendance data object
 * @param {Date} startDate - Start date for filtering
 * @param {Date} endDate - End date for filtering
 * @returns {Object} Summary statistics
 */
export function calculateSummaryStats(userData, startDate, endDate) {
  const { attendedDates, monthlyBreakdown } = filterDataByDateRange(userData, startDate, endDate);

  // Calculate totals from monthly breakdown
  const totalWorkingDays = monthlyBreakdown.reduce((sum, month) => sum + month.workingDays, 0);
  const daysAttended = monthlyBreakdown.reduce((sum, month) => sum + month.daysAttended, 0);
  const daysMissed = totalWorkingDays - daysAttended;

  // Calculate overall attendance percentage
  const attendancePercentage = totalWorkingDays > 0
    ? parseFloat(((daysAttended / totalWorkingDays) * 100).toFixed(2))
    : 0;

  return {
    attendancePercentage,
    totalWorkingDays,
    daysAttended,
    daysMissed
  };
}

/**
 * Transform monthly breakdown data for bar chart visualization
 * @param {Array} monthlyBreakdown - Array of monthly statistics
 * @returns {Array} Transformed data for chart rendering
 */
export function transformMonthlyData(monthlyBreakdown) {
  if (!Array.isArray(monthlyBreakdown)) {
    return [];
  }

  return monthlyBreakdown.map(month => ({
    month: getMonthLabel(month.month),
    monthKey: month.month,
    percentage: parseFloat(month.attendancePercentage.toFixed(2)),
    workingDays: month.workingDays,
    daysAttended: month.daysAttended,
    daysMissed: month.daysMissed
  }));
}
