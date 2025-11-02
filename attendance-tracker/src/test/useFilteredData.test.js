import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useFilteredData } from '../hooks/useFilteredData';

// Mock attendance data
const mockAttendanceData = {
  koustubh25: {
    attendanceDays: [
      '2025-10-09',
      '2025-10-10',
      '2025-11-01'
    ],
    statistics: {
      totalWorkingDays: 138,
      daysAttended: 6,
      daysMissed: 132,
      attendancePercentage: 4.35,
      monthlyBreakdown: [
        {
          month: '2025-10',
          workingDays: 23,
          daysAttended: 2,
          daysMissed: 21,
          attendancePercentage: 8.7
        },
        {
          month: '2025-11',
          workingDays: 20,
          daysAttended: 1,
          daysMissed: 19,
          attendancePercentage: 5.0
        }
      ]
    },
    targetStation: 'Southern Cross Station',
    lastUpdated: '2025-11-02T07:08:42Z'
  }
};

describe('useFilteredData Hook Tests', () => {
  it('should return filtered data with correct structure', () => {
    const startDate = new Date('2025-10-01');
    const endDate = new Date('2025-11-02');

    const { result } = renderHook(() =>
      useFilteredData(mockAttendanceData, 'koustubh25', startDate, endDate)
    );

    // Verify return structure
    expect(result.current).toHaveProperty('filteredMonthlyData');
    expect(result.current).toHaveProperty('summaryStats');
    expect(result.current).toHaveProperty('attendedDates');

    // Verify summary stats structure
    expect(result.current.summaryStats).toHaveProperty('attendancePercentage');
    expect(result.current.summaryStats).toHaveProperty('totalWorkingDays');
    expect(result.current.summaryStats).toHaveProperty('daysAttended');
    expect(result.current.summaryStats).toHaveProperty('daysMissed');

    // Verify monthly data is an array
    expect(Array.isArray(result.current.filteredMonthlyData)).toBe(true);

    // Verify attended dates is an array
    expect(Array.isArray(result.current.attendedDates)).toBe(true);
  });

  it('should filter data correctly for date range', () => {
    const startDate = new Date('2025-10-01');
    const endDate = new Date('2025-10-31');

    const { result } = renderHook(() =>
      useFilteredData(mockAttendanceData, 'koustubh25', startDate, endDate)
    );

    // Only October data should be included
    expect(result.current.filteredMonthlyData.length).toBe(1);
    expect(result.current.filteredMonthlyData[0].monthKey).toBe('2025-10');

    // Summary stats should reflect October only
    expect(result.current.summaryStats.totalWorkingDays).toBe(23);
    expect(result.current.summaryStats.daysAttended).toBe(2);
  });

  it('should handle null or undefined attendance data gracefully', () => {
    const startDate = new Date('2025-10-01');
    const endDate = new Date('2025-11-02');

    const { result } = renderHook(() =>
      useFilteredData(null, 'koustubh25', startDate, endDate)
    );

    // Should return empty/default values
    expect(result.current.filteredMonthlyData).toEqual([]);
    expect(result.current.attendedDates).toEqual([]);
    expect(result.current.summaryStats.attendancePercentage).toBe(0);
    expect(result.current.summaryStats.totalWorkingDays).toBe(0);
  });

  it('should memoize results for performance', () => {
    const startDate = new Date('2025-10-01');
    const endDate = new Date('2025-11-02');

    const { result, rerender } = renderHook(
      ({ data, user, start, end }) => useFilteredData(data, user, start, end),
      {
        initialProps: {
          data: mockAttendanceData,
          user: 'koustubh25',
          start: startDate,
          end: endDate
        }
      }
    );

    const firstResult = result.current;

    // Rerender with same props
    rerender({
      data: mockAttendanceData,
      user: 'koustubh25',
      start: startDate,
      end: endDate
    });

    // Should return same reference (memoized)
    expect(result.current.filteredMonthlyData).toBe(firstResult.filteredMonthlyData);
    expect(result.current.summaryStats).toBe(firstResult.summaryStats);
  });
});
