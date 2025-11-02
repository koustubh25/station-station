import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchAttendanceData } from '../utils/dataFetcher';
import { parseAttendanceDate, isDateInRange, getMonthLabel } from '../utils/dateHelpers';
import { filterDataByDateRange, calculateSummaryStats, transformMonthlyData } from '../utils/calculations';

// Mock attendance data based on actual structure
const mockAttendanceData = {
  metadata: {
    generatedAt: '2025-11-02T07:08:42Z',
    totalUsers: 1
  },
  koustubh25: {
    attendanceDays: [
      '2025-05-08',
      '2025-05-13',
      '2025-06-03',
      '2025-06-05',
      '2025-10-09',
      '2025-10-10'
    ],
    statistics: {
      totalWorkingDays: 138,
      daysAttended: 6,
      daysMissed: 132,
      attendancePercentage: 4.35,
      monthlyBreakdown: [
        {
          month: '2025-05',
          workingDays: 22,
          daysAttended: 2,
          daysMissed: 20,
          attendancePercentage: 9.09
        },
        {
          month: '2025-06',
          workingDays: 19,
          daysAttended: 2,
          daysMissed: 17,
          attendancePercentage: 10.53
        },
        {
          month: '2025-10',
          workingDays: 23,
          daysAttended: 2,
          daysMissed: 21,
          attendancePercentage: 8.7
        }
      ]
    },
    targetStation: 'Southern Cross Station',
    lastUpdated: '2025-11-02T07:08:42Z'
  }
};

describe('Data Layer Tests', () => {
  describe('fetchAttendanceData', () => {
    beforeEach(() => {
      global.fetch = vi.fn();
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('should fetch and return JSON data successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAttendanceData
      });

      const data = await fetchAttendanceData();

      expect(data).toEqual(mockAttendanceData);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({ cache: 'no-cache' })
      );
    });

    it('should handle network errors with descriptive messages', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(fetchAttendanceData()).rejects.toThrow('Failed to fetch attendance data');
    });
  });

  describe('Date Filtering', () => {
    it('should correctly filter dates within range', () => {
      const date = parseAttendanceDate('2025-06-15');
      const startDate = new Date('2025-06-01');
      const endDate = new Date('2025-06-30');

      expect(isDateInRange(date, startDate, endDate)).toBe(true);
    });

    it('should transform month string to readable label', () => {
      expect(getMonthLabel('2025-05')).toBe('May 2025');
      expect(getMonthLabel('2025-10')).toBe('October 2025');
    });
  });

  describe('Data Calculations', () => {
    it('should calculate correct summary statistics for date range', () => {
      const userData = mockAttendanceData.koustubh25;
      const startDate = new Date('2025-10-01');
      const endDate = new Date('2025-10-31');

      const stats = calculateSummaryStats(userData, startDate, endDate);

      expect(stats).toHaveProperty('attendancePercentage');
      expect(stats).toHaveProperty('totalWorkingDays');
      expect(stats).toHaveProperty('daysAttended');
      expect(stats).toHaveProperty('daysMissed');
      expect(stats.daysAttended).toBe(2); // Only October dates
    });

    it('should transform monthly breakdown data for bar chart', () => {
      const monthlyBreakdown = mockAttendanceData.koustubh25.statistics.monthlyBreakdown;
      const transformed = transformMonthlyData(monthlyBreakdown);

      expect(transformed).toBeInstanceOf(Array);
      expect(transformed.length).toBeGreaterThan(0);
      expect(transformed[0]).toHaveProperty('month');
      expect(transformed[0]).toHaveProperty('percentage');
      expect(transformed[0]).toHaveProperty('workingDays');
      expect(transformed[0]).toHaveProperty('daysAttended');
    });
  });
});
