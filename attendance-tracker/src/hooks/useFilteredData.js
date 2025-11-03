import { useMemo } from 'react';
import { filterDataByDateRange, calculateSummaryStats, transformMonthlyData } from '../utils/calculations';

/**
 * Custom hook for filtering attendance data by date range and user
 * Returns filtered monthly data, summary statistics, attended dates, manual attendance dates, and skip dates
 *
 * @param {Object} attendanceData - Full attendance data object
 * @param {string} selectedUser - Currently selected username
 * @param {Date} startDate - Start date for filtering
 * @param {Date} endDate - End date for filtering
 * @returns {Object} { filteredMonthlyData, summaryStats, attendedDates, manualAttendanceDates, skipDates }
 */
export function useFilteredData(attendanceData, selectedUser, startDate, endDate) {
  /**
   * Get user data from attendance data
   */
  const userData = useMemo(() => {
    if (!attendanceData || !selectedUser) {
      return null;
    }
    return attendanceData[selectedUser];
  }, [attendanceData, selectedUser]);

  /**
   * Get skip dates from user data
   */
  const skipDates = useMemo(() => {
    if (!userData || !userData.skipDates) {
      return [];
    }
    return userData.skipDates;
  }, [userData]);

  /**
   * Get manual attendance dates from user data
   */
  const manualAttendanceDates = useMemo(() => {
    if (!userData || !userData.manualAttendanceDates) {
      return [];
    }
    return userData.manualAttendanceDates;
  }, [userData]);

  /**
   * Filter data by date range
   */
  const { attendedDates, monthlyBreakdown } = useMemo(() => {
    if (!userData) {
      return { attendedDates: [], monthlyBreakdown: [] };
    }
    return filterDataByDateRange(userData, startDate, endDate);
  }, [userData, startDate, endDate]);

  /**
   * Calculate summary statistics
   */
  const summaryStats = useMemo(() => {
    if (!userData) {
      return {
        attendancePercentage: 0,
        totalWorkingDays: 0,
        daysAttended: 0,
        daysMissed: 0
      };
    }
    return calculateSummaryStats(userData, startDate, endDate);
  }, [userData, startDate, endDate]);

  /**
   * Transform monthly data for chart
   */
  const filteredMonthlyData = useMemo(() => {
    return transformMonthlyData(monthlyBreakdown);
  }, [monthlyBreakdown]);

  return {
    filteredMonthlyData,
    summaryStats,
    attendedDates,
    manualAttendanceDates,
    skipDates
  };
}
