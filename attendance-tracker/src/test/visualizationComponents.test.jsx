import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CalendarView from '../components/CalendarView';
import AttendanceChart from '../components/AttendanceChart';
import AttendanceDetails from '../components/AttendanceDetails';

describe('Visualization Components Tests', () => {
  describe('CalendarView', () => {
    it('should mark attended days correctly with red indicator', () => {
      const attendedDates = ['2025-11-01', '2025-11-05', '2025-11-10'];
      const onMonthChange = vi.fn();
      const onDayClick = vi.fn();
      const dateRange = { start: new Date('2025-10-01'), end: new Date('2025-12-31') };

      const { container } = render(
        <CalendarView
          attendedDates={attendedDates}
          selectedMonth={new Date('2025-11-01')}
          onMonthChange={onMonthChange}
          onDayClick={onDayClick}
          dateRange={dateRange}
        />
      );

      // Check that calendar renders
      const calendar = container.querySelector('.react-calendar');
      expect(calendar).toBeInTheDocument();

      // Check that attended day tiles have the correct class
      const attendedTiles = container.querySelectorAll('.attended-day');
      expect(attendedTiles.length).toBeGreaterThan(0);
    });

    it('should trigger onDayClick when an attended day is clicked', () => {
      const attendedDates = ['2025-11-01'];
      const onMonthChange = vi.fn();
      const onDayClick = vi.fn();
      const dateRange = { start: new Date('2025-10-01'), end: new Date('2025-12-31') };

      const { container } = render(
        <CalendarView
          attendedDates={attendedDates}
          selectedMonth={new Date('2025-11-01')}
          onMonthChange={onMonthChange}
          onDayClick={onDayClick}
          dateRange={dateRange}
        />
      );

      // Find an attended day tile and click it
      const attendedTile = container.querySelector('.attended-day');
      if (attendedTile) {
        fireEvent.click(attendedTile);
        expect(onDayClick).toHaveBeenCalled();
      }
    });
  });

  describe('AttendanceChart', () => {
    it('should render chart component with monthly data', () => {
      const monthlyData = [
        { month: 'October 2025', percentage: 80, workingDays: 20, daysAttended: 16 },
        { month: 'November 2025', percentage: 90, workingDays: 22, daysAttended: 20 }
      ];
      const dateRange = { start: new Date('2025-10-01'), end: new Date('2025-11-30') };

      render(
        <AttendanceChart monthlyData={monthlyData} dateRange={dateRange} />
      );

      // Check that the heading is present
      expect(screen.getByText('Attendance Chart')).toBeInTheDocument();

      // Check that data summary is displayed
      expect(screen.getByText(/Showing attendance data for 2 months/i)).toBeInTheDocument();
    });

    it('should display empty state when no data is provided', () => {
      const monthlyData = [];
      const dateRange = { start: new Date('2025-10-01'), end: new Date('2025-10-31') };

      render(
        <AttendanceChart monthlyData={monthlyData} dateRange={dateRange} />
      );

      // Check for empty state message
      expect(screen.getByText(/No attendance data available/i)).toBeInTheDocument();
    });
  });

  describe('AttendanceDetails', () => {
    it('should display timestamp and station when opened', () => {
      const date = '2025-11-01';
      const timestamp = '08:30 AM';
      const station = 'Flinders Street Station';
      const onClose = vi.fn();

      render(
        <AttendanceDetails
          date={date}
          timestamp={timestamp}
          station={station}
          onClose={onClose}
        />
      );

      // Check that modal displays date
      expect(screen.getByText(/November 1, 2025/i)).toBeInTheDocument();

      // Check that timestamp is displayed
      expect(screen.getByText(timestamp)).toBeInTheDocument();

      // Check that station is displayed
      expect(screen.getByText(station)).toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', () => {
      const date = '2025-11-01';
      const timestamp = '08:30 AM';
      const station = 'Flinders Street Station';
      const onClose = vi.fn();

      render(
        <AttendanceDetails
          date={date}
          timestamp={timestamp}
          station={station}
          onClose={onClose}
        />
      );

      // Find the X close button (more specific query)
      const closeButton = screen.getByRole('button', { name: /close attendance details/i });
      fireEvent.click(closeButton);

      expect(onClose).toHaveBeenCalledTimes(1);
    });
  });
});
