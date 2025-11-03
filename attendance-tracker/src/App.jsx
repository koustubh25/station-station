import { useState, useEffect, useMemo } from 'react';
import { useAttendanceData } from './hooks/useAttendanceData';
import { useFilteredData } from './hooks/useFilteredData';
import { DEFAULT_START_DATE, DEFAULT_END_DATE } from './constants/config';
import { formatDateRange } from './utils/dateHelpers';

// Component imports
import UserSelector from './components/UserSelector';
import CalendarView from './components/CalendarView';
import AttendanceChart from './components/AttendanceChart';
import DateRangeFilter from './components/DateRangeFilter';
import SummaryStats from './components/SummaryStats';
import AttendanceDetails from './components/AttendanceDetails';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

/**
 * Main App Component - Attendance Tracker Application
 *
 * Integrates all components to provide a complete attendance tracking
 * and visualization experience with responsive design and accessibility.
 *
 * @returns {JSX.Element} Main application component
 */
function App() {
  // Fetch attendance data from GitHub
  const { data, loading, error, refetch } = useAttendanceData();

  // State management
  const [selectedUser, setSelectedUser] = useState('');
  const [startDate, setStartDate] = useState(DEFAULT_START_DATE);
  const [endDate, setEndDate] = useState(DEFAULT_END_DATE);
  const [selectedAttendanceDay, setSelectedAttendanceDay] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(new Date());

  // Get list of users from data
  const users = useMemo(() => {
    if (!data) return [];
    return Object.keys(data).filter(key => key !== 'metadata');
  }, [data]);

  // Set initial selected user when data loads
  useEffect(() => {
    if (users.length > 0 && !selectedUser) {
      setSelectedUser(users[0]);
    }
  }, [users, selectedUser]);

  // Get filtered data for selected user and date range
  const { filteredMonthlyData, summaryStats, attendedDates, manualAttendanceDates, skipDates } = useFilteredData(
    data,
    selectedUser,
    startDate,
    endDate
  );

  // Format date range for display
  const dateRangeText = useMemo(() => {
    return formatDateRange(startDate, endDate);
  }, [startDate, endDate]);

  /**
   * Handle user selection change
   */
  const handleUserChange = (username) => {
    setSelectedUser(username);
    setSelectedAttendanceDay(null); // Clear any open modal
  };

  /**
   * Handle date range changes
   */
  const handleStartDateChange = (date) => {
    setStartDate(date);
  };

  const handleEndDateChange = (date) => {
    setEndDate(date);
  };

  /**
   * Handle calendar month navigation
   */
  const handleMonthChange = (newMonth) => {
    setSelectedMonth(newMonth);
  };

  /**
   * Handle attended day click - show details modal
   * Supports both PTV attendance and manual attendance
   */
  const handleDayClick = (dateString) => {
    if (!data || !selectedUser) return;

    const userData = data[selectedUser];
    if (!userData) return;

    // Check if this is manual attendance
    const isManual = userData.manualAttendanceDates && userData.manualAttendanceDates.includes(dateString);

    if (isManual) {
      // Manual attendance - no timestamp
      setSelectedAttendanceDay({
        date: dateString,
        timestamp: null,
        station: userData.targetStation || 'Unknown',
        isManual: true
      });
    } else {
      // PTV attendance - find the attendance record
      if (!userData.attendanceDays) return;

      const attendanceRecord = userData.attendanceDays.find(
        (record) => record.date === dateString
      );

      if (attendanceRecord) {
        setSelectedAttendanceDay({
          date: dateString,
          timestamp: attendanceRecord.timestamp,
          station: attendanceRecord.targetStation || userData.targetStation || 'Unknown',
          isManual: false
        });
      }
    }
  };

  /**
   * Close attendance details modal
   */
  const handleCloseModal = () => {
    setSelectedAttendanceDay(null);
  };

  /**
   * Get last updated timestamp from metadata
   */
  const lastUpdated = useMemo(() => {
    if (!data || !data.metadata || !data.metadata.lastUpdated) {
      return null;
    }
    const date = new Date(data.metadata.lastUpdated);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }, [data]);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <LoadingSpinner />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ErrorMessage message={error} onRetry={refetch} />
      </div>
    );
  }

  // No data state
  if (!data || users.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ErrorMessage
          message="No attendance data available. Please check the data source."
          onRetry={refetch}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main container with responsive padding */}
      <main className="container mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Header section */}
        <header className="mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
            Attendance Tracker
          </h1>
          {lastUpdated && (
            <p className="text-sm text-gray-600">
              Last updated: {lastUpdated}
            </p>
          )}
        </header>

        {/* User selector section */}
        <section className="mb-6" aria-label="User selection">
          <UserSelector
            users={users}
            selectedUser={selectedUser}
            onUserChange={handleUserChange}
          />
        </section>

        {/* Date range filter section */}
        <section className="mb-6" aria-label="Date range filter">
          <DateRangeFilter
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={handleStartDateChange}
            onEndDateChange={handleEndDateChange}
          />
        </section>

        {/* Summary statistics section */}
        <section className="mb-6" aria-label="Attendance summary">
          <SummaryStats
            statistics={summaryStats}
            dateRange={dateRangeText}
          />
        </section>

        {/* Data visualization section - responsive grid layout */}
        <section
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6"
          aria-label="Attendance visualizations"
        >
          {/* Calendar view */}
          <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 border border-gray-200">
            <CalendarView
              attendedDates={attendedDates}
              manualAttendanceDates={manualAttendanceDates}
              skipDates={skipDates}
              selectedMonth={selectedMonth}
              onMonthChange={handleMonthChange}
              onDayClick={handleDayClick}
              dateRange={{ start: startDate, end: endDate }}
            />
          </div>

          {/* Attendance chart */}
          <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 border border-gray-200">
            <AttendanceChart
              monthlyData={filteredMonthlyData}
              dateRange={{ start: startDate, end: endDate }}
            />
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-600">
          <p>
            Built with React, Tailwind CSS, Recharts, and react-calendar
          </p>
        </footer>
      </main>

      {/* Attendance details modal (conditional) */}
      {selectedAttendanceDay && (
        <AttendanceDetails
          date={selectedAttendanceDay.date}
          timestamp={selectedAttendanceDay.timestamp}
          station={selectedAttendanceDay.station}
          isManual={selectedAttendanceDay.isManual}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
}

export default App;
