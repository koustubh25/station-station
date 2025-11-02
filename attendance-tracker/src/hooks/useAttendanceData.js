import { useState, useEffect } from 'react';
import { fetchAttendanceData } from '../utils/dataFetcher';

/**
 * Custom hook for fetching and managing attendance data
 * @returns {Object} { data, loading, error, refetch }
 */
export function useAttendanceData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch attendance data from the API
   */
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const attendanceData = await fetchAttendanceData();
      setData(attendanceData);
    } catch (err) {
      setError(err.message || 'Failed to load attendance data');
      console.error('Error loading attendance data:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Refetch data (for retry functionality)
   */
  const refetch = () => {
    loadData();
  };

  // Fetch data on mount
  useEffect(() => {
    loadData();
  }, []);

  return {
    data,
    loading,
    error,
    refetch
  };
}
