import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import UserSelector from '../components/UserSelector';
import SummaryStats from '../components/SummaryStats';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

describe('UI Components Tests', () => {
  describe('UserSelector', () => {
    it('should render all usernames in dropdown', () => {
      const users = ['john', 'jane', 'alice'];
      const selectedUser = 'john';
      const onUserChange = vi.fn();

      render(
        <UserSelector
          users={users}
          selectedUser={selectedUser}
          onUserChange={onUserChange}
        />
      );

      // Check that select element exists
      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();

      // Check that all users are in options
      users.forEach(user => {
        expect(screen.getByText(user)).toBeInTheDocument();
      });
    });

    it('should call onChange when user selection changes', () => {
      const users = ['john', 'jane', 'alice'];
      const selectedUser = 'john';
      const onUserChange = vi.fn();

      render(
        <UserSelector
          users={users}
          selectedUser={selectedUser}
          onUserChange={onUserChange}
        />
      );

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'jane' } });

      expect(onUserChange).toHaveBeenCalledWith('jane');
    });
  });

  describe('SummaryStats', () => {
    it('should display all required metrics correctly', () => {
      const statistics = {
        attendancePercentage: 85.25,
        totalWorkingDays: 120,
        daysAttended: 102,
        daysMissed: 18
      };

      const dateRange = 'Oct 01, 2025 - Nov 02, 2025';

      render(
        <SummaryStats statistics={statistics} dateRange={dateRange} />
      );

      // Check that attendance percentage is displayed
      expect(screen.getByText(/85\.25%/)).toBeInTheDocument();

      // Check date range
      expect(screen.getByText(dateRange)).toBeInTheDocument();

      // Check total working days (using text matcher for better specificity)
      expect(screen.getByText('120')).toBeInTheDocument();

      // Check days attended
      expect(screen.getByText('102')).toBeInTheDocument();

      // Check days missed
      expect(screen.getByText('18')).toBeInTheDocument();

      // Verify the labels are present
      expect(screen.getByText(/Working Days/i)).toBeInTheDocument();
      expect(screen.getByText(/Days Attended/i)).toBeInTheDocument();
      expect(screen.getByText(/Days Missed/i)).toBeInTheDocument();
    });
  });

  describe('LoadingSpinner', () => {
    it('should render with accessible loading message', () => {
      render(<LoadingSpinner />);

      // Check for accessible loading message
      const loadingMessage = screen.getByText(/loading/i);
      expect(loadingMessage).toBeInTheDocument();
    });
  });

  describe('ErrorMessage', () => {
    it('should render error message and retry button when onRetry provided', () => {
      const message = 'Failed to load data';
      const onRetry = vi.fn();

      render(<ErrorMessage message={message} onRetry={onRetry} />);

      // Check error message is displayed
      expect(screen.getByText(message)).toBeInTheDocument();

      // Check retry button exists and can be clicked
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();

      fireEvent.click(retryButton);
      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it('should render error message without retry button when onRetry not provided', () => {
      const message = 'An error occurred';

      render(<ErrorMessage message={message} />);

      // Check error message is displayed
      expect(screen.getByText(message)).toBeInTheDocument();

      // Check no retry button exists
      const retryButton = screen.queryByRole('button', { name: /retry/i });
      expect(retryButton).not.toBeInTheDocument();
    });
  });
});
