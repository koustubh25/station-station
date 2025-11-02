import { useMemo } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { DEFAULT_START_DATE, DEFAULT_END_DATE } from '../constants/config';

/**
 * DateRangeFilter Component
 *
 * Provides two date picker inputs for filtering data by date range.
 * Validates that end date is not before start date and shows error message if invalid.
 *
 * @param {Object} props - Component props
 * @param {Date} props.startDate - Start date for filtering (default: October 1, 2025)
 * @param {Date} props.endDate - End date for filtering (default: current date)
 * @param {Function} props.onStartDateChange - Callback when start date changes
 * @param {Function} props.onEndDateChange - Callback when end date changes
 * @returns {JSX.Element} DateRangeFilter component
 */
function DateRangeFilter({
  startDate = DEFAULT_START_DATE,
  endDate = DEFAULT_END_DATE,
  onStartDateChange,
  onEndDateChange
}) {
  /**
   * Validate that end date is not before start date
   */
  const isInvalidRange = useMemo(() => {
    return endDate < startDate;
  }, [startDate, endDate]);

  /**
   * Handle start date change
   */
  const handleStartDateChange = (date) => {
    if (date && onStartDateChange) {
      onStartDateChange(date);
    }
  };

  /**
   * Handle end date change
   */
  const handleEndDateChange = (date) => {
    if (date && onEndDateChange) {
      onEndDateChange(date);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Date Range Filter
      </h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {/* Start Date Picker */}
        <div>
          <label
            htmlFor="start-date-picker"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Start Date
          </label>
          <DatePicker
            id="start-date-picker"
            selected={startDate}
            onChange={handleStartDateChange}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            dateFormat="MMM dd, yyyy"
            className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-attended focus:border-attended
                       text-base bg-white cursor-pointer
                       hover:border-gray-400 transition-colors"
            wrapperClassName="w-full"
            aria-label="Select start date for filtering"
          />
        </div>

        {/* End Date Picker */}
        <div>
          <label
            htmlFor="end-date-picker"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            End Date
          </label>
          <DatePicker
            id="end-date-picker"
            selected={endDate}
            onChange={handleEndDateChange}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            dateFormat="MMM dd, yyyy"
            className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm
                       focus:outline-none focus:ring-2 focus:ring-attended focus:border-attended
                       text-base bg-white cursor-pointer
                       hover:border-gray-400 transition-colors"
            wrapperClassName="w-full"
            aria-label="Select end date for filtering"
          />
        </div>
      </div>

      {/* Validation Error Message */}
      {isInvalidRange && (
        <div
          className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm"
          role="alert"
          aria-live="polite"
        >
          End date cannot be before start date. Please select a valid date range.
        </div>
      )}
    </div>
  );
}

export default DateRangeFilter;
