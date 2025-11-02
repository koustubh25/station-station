import { useMemo } from 'react';
import Holidays from 'date-holidays';

/**
 * Custom hook to get public holidays for Victoria, Australia
 * Returns a Set of holiday dates in YYYY-MM-DD format
 *
 * @param {Date} startDate - Start date for holiday range
 * @param {Date} endDate - End date for holiday range
 * @returns {Set<string>} Set of holiday dates in YYYY-MM-DD format
 */
export function usePublicHolidays(startDate, endDate) {
  const publicHolidays = useMemo(() => {
    const hd = new Holidays('AU', 'VIC'); // Australia, Victoria
    const holidaySet = new Set();

    if (!startDate || !endDate) {
      return holidaySet;
    }

    // Get start and end years
    const startYear = startDate.getFullYear();
    const endYear = endDate.getFullYear();

    // Get holidays for each year in range
    for (let year = startYear; year <= endYear; year++) {
      const holidays = hd.getHolidays(year);

      holidays.forEach(holiday => {
        const holidayDate = new Date(holiday.date);

        // Only include if within our date range
        if (holidayDate >= startDate && holidayDate <= endDate) {
          // Convert to YYYY-MM-DD format using local timezone
          const dateString = holidayDate.toLocaleDateString('en-CA');
          holidaySet.add(dateString);
        }
      });
    }

    return holidaySet;
  }, [startDate, endDate]);

  return publicHolidays;
}
