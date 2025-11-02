/**
 * SummaryStats Component
 *
 * Displays attendance summary statistics in a card layout.
 * Shows total attendance percentage, date range, working days, attended days, and missed days.
 *
 * @param {Object} props - Component props
 * @param {Object} props.statistics - Statistics object containing attendance metrics
 * @param {number} props.statistics.attendancePercentage - Overall attendance percentage
 * @param {number} props.statistics.totalWorkingDays - Total number of working days
 * @param {number} props.statistics.daysAttended - Number of days attended
 * @param {number} props.statistics.daysMissed - Number of days missed
 * @param {string} props.dateRange - Formatted date range string (e.g., "Oct 01, 2025 - Nov 02, 2025")
 * @returns {JSX.Element} SummaryStats component
 */
function SummaryStats({ statistics, dateRange }) {
  const {
    attendancePercentage,
    totalWorkingDays,
    daysAttended,
    daysMissed
  } = statistics;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Attendance Summary
      </h2>

      {/* Main metric - Attendance Percentage */}
      <div className="mb-6 text-center">
        <div
          className="text-5xl font-bold text-attended mb-2"
          aria-label={`Attendance percentage: ${attendancePercentage}%`}
        >
          {attendancePercentage}%
        </div>
        <p className="text-sm text-gray-600">Total Attendance</p>
      </div>

      {/* Date Range */}
      <div className="mb-4 pb-4 border-b border-gray-200">
        <p className="text-sm text-gray-600 mb-1">Period</p>
        <p className="text-base font-medium text-gray-800">{dateRange}</p>
      </div>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {/* Working Days */}
        <div className="text-center p-3 bg-gray-50 rounded-md">
          <p className="text-2xl font-bold text-gray-800">{totalWorkingDays}</p>
          <p className="text-xs text-gray-600 mt-1">Working Days</p>
        </div>

        {/* Days Attended */}
        <div className="text-center p-3 bg-green-50 rounded-md">
          <p className="text-2xl font-bold text-green-700">{daysAttended}</p>
          <p className="text-xs text-gray-600 mt-1">Days Attended</p>
        </div>

        {/* Days Missed */}
        <div className="text-center p-3 bg-red-50 rounded-md">
          <p className="text-2xl font-bold text-red-700">{daysMissed}</p>
          <p className="text-xs text-gray-600 mt-1">Days Missed</p>
        </div>
      </div>
    </div>
  );
}

export default SummaryStats;
