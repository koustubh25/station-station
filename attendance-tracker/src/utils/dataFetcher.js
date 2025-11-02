import { ATTENDANCE_JSON_URL } from '../constants/config';

/**
 * Fetches attendance data from GitHub raw URL
 * @returns {Promise<Object>} The attendance data JSON object
 * @throws {Error} If fetch fails or JSON is invalid
 */
export async function fetchAttendanceData() {
  try {
    const response = await fetch(ATTENDANCE_JSON_URL, {
      cache: 'no-cache',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Validate basic JSON structure
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid JSON structure');
    }

    if (!data.metadata) {
      throw new Error('Missing metadata in JSON');
    }

    return data;
  } catch (error) {
    console.error('Error fetching attendance data:', error);
    throw new Error('Failed to fetch attendance data. Please check your connection and try again.');
  }
}
