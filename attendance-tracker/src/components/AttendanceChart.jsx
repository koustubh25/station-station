import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ATTENDED_DAY_COLOR } from '../constants/config';

/**
 * AttendanceChart component - Bar chart showing monthly attendance percentages
 *
 * @component
 * @param {Object} props - Component props
 * @param {Array} props.monthlyData - Array of monthly attendance data
 * @param {Object} props.monthlyData[] - Monthly data object
 * @param {string} props.monthlyData[].month - Month label (e.g., "October 2025")
 * @param {number} props.monthlyData[].percentage - Attendance percentage (0-100)
 * @param {number} props.monthlyData[].workingDays - Total working days in month
 * @param {number} props.monthlyData[].daysAttended - Days attended in month
 * @param {Object} props.dateRange - Date range filter { start: Date, end: Date }
 * @returns {JSX.Element} Bar chart component
 */
function AttendanceChart({ monthlyData = [], dateRange }) {
  /**
   * Custom tooltip component for chart
   * Shows detailed information on hover
   */
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border border-gray-300 rounded-lg shadow-lg p-4">
          <p className="font-semibold text-gray-900 mb-2">{data.month}</p>
          <p className="text-sm text-gray-700">
            <span className="font-medium">Attendance:</span> {data.percentage}%
          </p>
          <p className="text-sm text-gray-700">
            <span className="font-medium">Working Days:</span> {data.workingDays}
          </p>
          <p className="text-sm text-gray-700">
            <span className="font-medium">Days Attended:</span> {data.daysAttended}
          </p>
        </div>
      );
    }
    return null;
  };

  /**
   * Format month labels for X-axis
   * Shortens month names on mobile devices
   */
  const formatXAxisLabel = (value) => {
    // On mobile, show abbreviated month (e.g., "Oct 2025")
    if (window.innerWidth < 640) {
      const parts = value.split(' ');
      if (parts.length === 2) {
        return `${parts[0].slice(0, 3)} ${parts[1]}`;
      }
    }
    return value;
  };

  // If no data, show empty state
  if (!monthlyData || monthlyData.length === 0) {
    return (
      <div className="chart-container">
        <h2 className="text-xl font-semibold mb-4">Attendance Chart</h2>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-gray-500">No attendance data available for selected date range</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h2 className="text-xl font-semibold mb-4">Attendance Chart</h2>
      <div className="w-full h-64 md:h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={monthlyData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 12 }}
              tickFormatter={formatXAxisLabel}
              label={{ value: 'Month', position: 'insideBottom', offset: -10, style: { fontSize: 14, fontWeight: 600 } }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12 }}
              label={{ value: 'Attendance %', angle: -90, position: 'insideLeft', style: { fontSize: 14, fontWeight: 600 } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="percentage"
              fill={ATTENDED_DAY_COLOR}
              radius={[8, 8, 0, 0]}
              maxBarSize={60}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 text-sm text-gray-600 text-center">
        <p>Showing attendance data for {monthlyData.length} month{monthlyData.length !== 1 ? 's' : ''}</p>
      </div>
    </div>
  );
}

export default AttendanceChart;
