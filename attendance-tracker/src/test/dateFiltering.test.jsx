import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DateRangeFilter from '../components/DateRangeFilter';

describe('Date Filtering Tests', () => {
  describe('DateRangeFilter', () => {
    it('should render two date pickers with labels', () => {
      const startDate = new Date('2025-10-01');
      const endDate = new Date('2025-11-02');
      const onStartDateChange = vi.fn();
      const onEndDateChange = vi.fn();

      render(
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={onStartDateChange}
          onEndDateChange={onEndDateChange}
        />
      );

      // Check for Start Date label
      expect(screen.getByText('Start Date')).toBeInTheDocument();

      // Check for End Date label
      expect(screen.getByText('End Date')).toBeInTheDocument();

      // Check for date picker inputs
      const inputs = screen.getAllByRole('textbox');
      expect(inputs).toHaveLength(2);
    });

    it('should validate that end date is not before start date', () => {
      const startDate = new Date('2025-10-01');
      const endDate = new Date('2025-09-01'); // Invalid: before start date
      const onStartDateChange = vi.fn();
      const onEndDateChange = vi.fn();

      render(
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={onStartDateChange}
          onEndDateChange={onEndDateChange}
        />
      );

      // Check for validation error message
      expect(screen.getByText(/End date cannot be before start date/i)).toBeInTheDocument();
    });

    it('should set default dates correctly', () => {
      const onStartDateChange = vi.fn();
      const onEndDateChange = vi.fn();

      render(
        <DateRangeFilter
          onStartDateChange={onStartDateChange}
          onEndDateChange={onEndDateChange}
        />
      );

      // Component should render without errors with default dates
      const inputs = screen.getAllByRole('textbox');
      expect(inputs).toHaveLength(2);
    });

    it('should not show error message when date range is valid', () => {
      const startDate = new Date('2025-10-01');
      const endDate = new Date('2025-11-02');
      const onStartDateChange = vi.fn();
      const onEndDateChange = vi.fn();

      render(
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={onStartDateChange}
          onEndDateChange={onEndDateChange}
        />
      );

      // Check that no error message is present
      const errorMessage = screen.queryByText(/End date cannot be before start date/i);
      expect(errorMessage).not.toBeInTheDocument();
    });
  });
});
