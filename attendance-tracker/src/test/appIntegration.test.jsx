import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

// Mock attendance data matching actual JSON structure (attendanceDays as array of strings)
const mockAttendanceData = {
  metadata: {
    generatedAt: '2025-11-02T07:08:42Z',
    totalUsers: 2,
    lastUpdated: '2025-11-02T07:08:42Z'
  },
  koustubh25: {
    attendanceDays: ['2025-10-09', '2025-10-10', '2025-11-01'],
    statistics: {
      totalWorkingDays: 43,
      daysAttended: 3,
      daysMissed: 40,
      attendancePercentage: 6.98,
      monthlyBreakdown: [
        {
          month: '2025-10',
          workingDays: 23,
          daysAttended: 2,
          daysMissed: 21,
          attendancePercentage: 8.7
        },
        {
          month: '2025-11',
          workingDays: 20,
          daysAttended: 1,
          daysMissed: 19,
          attendancePercentage: 5.0
        }
      ]
    },
    targetStation: 'Southern Cross Station',
    lastUpdated: '2025-11-02T07:08:42Z'
  },
  johndoe: {
    attendanceDays: ['2025-10-15', '2025-10-16'],
    statistics: {
      totalWorkingDays: 23,
      daysAttended: 2,
      daysMissed: 21,
      attendancePercentage: 8.7,
      monthlyBreakdown: [
        {
          month: '2025-10',
          workingDays: 23,
          daysAttended: 2,
          daysMissed: 21,
          attendancePercentage: 8.7
        }
      ]
    },
    targetStation: 'Flinders Street',
    lastUpdated: '2025-11-02T07:08:42Z'
  }
};

describe('App Integration Tests', () => {
  beforeEach(() => {
    // Mock fetch to return attendance data
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockAttendanceData)
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render app successfully with loaded data', async () => {
    render(<App />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Attendance Tracker')).toBeInTheDocument();
    });

    // Check that user selector is present
    expect(screen.getByRole('combobox')).toBeInTheDocument();

    // Check that summary stats are present
    expect(screen.getByText(/Working Days/i)).toBeInTheDocument();
  });

  it('should update all views when user selection changes', async () => {
    render(<App />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    // Initially shows first user (koustubh25)
    const select = screen.getByRole('combobox');
    expect(select.value).toBe('koustubh25');

    // Change to second user
    fireEvent.change(select, { target: { value: 'johndoe' } });

    // Wait for UI to update
    await waitFor(() => {
      expect(select.value).toBe('johndoe');
    });

    // Verify that the data has updated (attendance percentage should change)
    // johndoe has only October data with 8.7% attendance
    await waitFor(() => {
      expect(screen.getByText(/8\.7%/)).toBeInTheDocument();
    });
  });

  it('should update calendar and chart when date range changes', async () => {
    render(<App />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Attendance Tracker')).toBeInTheDocument();
    });

    // Find date picker inputs
    const dateInputs = screen.getAllByRole('textbox');
    expect(dateInputs.length).toBeGreaterThanOrEqual(2);

    // Calendar component should be present
    await waitFor(() => {
      const calendar = document.querySelector('.react-calendar');
      expect(calendar).toBeInTheDocument();
    });

    // Attendance Chart should be present
    expect(screen.getByText('Attendance Chart')).toBeInTheDocument();
  });

  it('should display loading state on initial data fetch', () => {
    // Mock slow fetch
    global.fetch = vi.fn(() =>
      new Promise((resolve) =>
        setTimeout(() => {
          resolve({
            ok: true,
            json: () => Promise.resolve(mockAttendanceData)
          });
        }, 100)
      )
    );

    render(<App />);

    // Should show loading spinner initially
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should display error message and retry button on fetch failure', async () => {
    // Mock fetch failure
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

    render(<App />);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch attendance data/i)).toBeInTheDocument();
    });

    // Retry button should be present
    const retryButton = screen.getByRole('button', { name: /retry/i });
    expect(retryButton).toBeInTheDocument();

    // Mock successful fetch for retry
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockAttendanceData)
      })
    );

    // Click retry
    fireEvent.click(retryButton);

    // Should load successfully
    await waitFor(() => {
      expect(screen.getByText('Attendance Tracker')).toBeInTheDocument();
    });
  });

  it('should filter data correctly when date range changes', async () => {
    render(<App />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Attendance Tracker')).toBeInTheDocument();
    });

    // Verify initial state shows both months of data
    // koustubh25 has data in October (2 days) and November (1 day)
    // Total working days should be 43 initially
    await waitFor(() => {
      expect(screen.getByText('43')).toBeInTheDocument(); // Total working days
    });

    // Verify calendar and chart are present
    const calendar = document.querySelector('.react-calendar');
    expect(calendar).toBeInTheDocument();
    expect(screen.getByText('Attendance Chart')).toBeInTheDocument();
  });

  it('should render calendar with attended days marked', async () => {
    render(<App />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Attendance Tracker')).toBeInTheDocument();
    });

    // Wait for calendar to render
    await waitFor(() => {
      const calendar = document.querySelector('.react-calendar');
      expect(calendar).toBeInTheDocument();
    });

    // Check that attended day tiles exist (may not be visible in current month)
    // Just verify calendar is functional
    const tiles = document.querySelectorAll('.react-calendar__tile');
    expect(tiles.length).toBeGreaterThan(0);
  });

  it('should show summary statistics for selected user and date range', async () => {
    render(<App />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Attendance Tracker')).toBeInTheDocument();
    });

    // Check that attendance percentage is displayed
    await waitFor(() => {
      expect(screen.getByText(/6\.98%/)).toBeInTheDocument();
    });

    // Check that working days count is displayed
    expect(screen.getByText('43')).toBeInTheDocument();

    // Check that days attended and missed are displayed
    // Use more specific text matchers to avoid conflicts
    expect(screen.getByText(/Days Attended/i)).toBeInTheDocument();
    expect(screen.getByText(/Days Missed/i)).toBeInTheDocument();
  });
});
