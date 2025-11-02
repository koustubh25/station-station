import { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { ATTENDED_DAY_COLOR } from '../constants/config';
import { usePublicHolidays } from '../hooks/usePublicHolidays';

/**
 * CalendarView component - Monthly calendar with attended days marked in red
 *
 * @component
 * @param {Object} props - Component props
 * @param {string[]} props.attendedDates - Array of attended dates in YYYY-MM-DD format
 * @param {string[]} props.skipDates - Array of skip dates in YYYY-MM-DD format
 * @param {Date} props.selectedMonth - Currently selected month to display
 * @param {Function} props.onMonthChange - Callback when month navigation occurs
 * @param {Function} props.onDayClick - Callback when an attended day is clicked
 * @param {Object} props.dateRange - Date range filter { start: Date, end: Date }
 * @returns {JSX.Element} Calendar component
 */
function CalendarView({ attendedDates = [], skipDates = [], selectedMonth, onMonthChange, onDayClick, dateRange }) {
  const [activeStartDate, setActiveStartDate] = useState(selectedMonth || new Date());

  // Get public holidays for Victoria, Australia
  const publicHolidays = usePublicHolidays(dateRange?.start, dateRange?.end);

  // Update active date when selectedMonth prop changes
  useEffect(() => {
    if (selectedMonth) {
      setActiveStartDate(selectedMonth);
    }
  }, [selectedMonth]);

  /**
   * Determine the CSS class for calendar tiles
   * Marks attended days with red background, skip dates with amber text, and public holidays with red text
   */
  const tileClassName = ({ date, view }) => {
    // Only apply classes to month view (not year/decade view)
    if (view !== 'month') {
      return null;
    }

    // Use local date format to avoid timezone conversion issues
    const dateString = date.toLocaleDateString('en-CA'); // YYYY-MM-DD format
    const isAttended = attendedDates.includes(dateString);
    const isSkipDate = skipDates.includes(dateString);
    const isPublicHoliday = publicHolidays.has(dateString);

    if (isAttended) {
      return 'attended-day';
    } else if (isSkipDate) {
      return 'skip-date';
    } else if (isPublicHoliday) {
      return 'public-holiday';
    }

    return null;
  };

  /**
   * Handle date click events
   * Only trigger callback for attended days
   */
  const handleClickDay = (value) => {
    // Use local date format to avoid timezone conversion issues
    const dateString = value.toLocaleDateString('en-CA'); // YYYY-MM-DD format
    const isAttended = attendedDates.includes(dateString);

    if (isAttended && onDayClick) {
      onDayClick(dateString);
    }
  };

  /**
   * Handle active start date change (month navigation)
   */
  const handleActiveStartDateChange = ({ activeStartDate, view }) => {
    if (view === 'month' && activeStartDate) {
      setActiveStartDate(activeStartDate);
      if (onMonthChange) {
        onMonthChange(activeStartDate);
      }
    }
  };

  return (
    <div className="calendar-view-container">
      <h2 className="text-xl font-semibold mb-4">Attendance Calendar</h2>
      <div className="calendar-wrapper">
        <Calendar
          activeStartDate={activeStartDate}
          onActiveStartDateChange={handleActiveStartDateChange}
          onClickDay={handleClickDay}
          tileClassName={tileClassName}
          minDate={dateRange?.start}
          maxDate={dateRange?.end}
          showNeighboringMonth={false}
          className="w-full"
        />
      </div>
      <style>{`
        .attended-day {
          background-color: ${ATTENDED_DAY_COLOR} !important;
          color: white !important;
          border-radius: 50%;
        }

        .attended-day:hover {
          background-color: #dc2626 !important;
          cursor: pointer;
        }

        .skip-date {
          color: #f59e0b !important;
          font-weight: 600;
        }

        .public-holiday {
          color: #ef4444 !important;
        }

        .react-calendar {
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          padding: 1rem;
          font-family: inherit;
        }

        .react-calendar__navigation button {
          min-width: 44px;
          min-height: 44px;
          background: none;
          font-size: 1rem;
          font-weight: 600;
        }

        .react-calendar__navigation button:enabled:hover,
        .react-calendar__navigation button:enabled:focus {
          background-color: #f3f4f6;
          border-radius: 0.375rem;
        }

        .react-calendar__tile {
          min-width: 44px;
          min-height: 44px;
          padding: 0.75rem 0.5rem;
          font-size: 0.875rem;
        }

        .react-calendar__tile:enabled:hover,
        .react-calendar__tile:enabled:focus {
          background-color: #f3f4f6;
          border-radius: 0.375rem;
        }

        .react-calendar__tile--active {
          background: #3b82f6 !important;
          color: white !important;
          border-radius: 0.375rem;
        }

        .react-calendar__tile--now {
          background: #fef3c7;
          border-radius: 0.375rem;
        }

        .react-calendar__month-view__weekdays {
          text-transform: uppercase;
          font-size: 0.75rem;
          font-weight: 600;
          color: #6b7280;
        }

        /* Red text for weekends to distinguish them from weekdays */
        .react-calendar__month-view__days__day--weekend {
          color: #ef4444;
        }

        @media (max-width: 640px) {
          .react-calendar__tile {
            padding: 0.5rem 0.25rem;
            font-size: 0.75rem;
          }

          .react-calendar__navigation button {
            font-size: 0.875rem;
          }
        }
      `}</style>
    </div>
  );
}

export default CalendarView;
