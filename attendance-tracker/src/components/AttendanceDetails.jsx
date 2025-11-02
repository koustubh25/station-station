import { useEffect, useRef } from 'react';

/**
 * AttendanceDetails component - Modal displaying detailed attendance information for a specific day
 *
 * @component
 * @param {Object} props - Component props
 * @param {string} props.date - Date in YYYY-MM-DD format
 * @param {string} props.timestamp - Time of attendance (e.g., "08:30 AM")
 * @param {string} props.station - Station name
 * @param {Function} props.onClose - Callback to close the modal
 * @returns {JSX.Element} Modal component
 */
function AttendanceDetails({ date, timestamp, station, onClose }) {
  const modalRef = useRef(null);
  const closeButtonRef = useRef(null);

  /**
   * Format date string for display
   * Converts YYYY-MM-DD to "Month Day, Year"
   */
  const formatDate = (dateString) => {
    const dateObj = new Date(dateString + 'T00:00:00'); // Add time to avoid timezone issues
    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  /**
   * Handle keyboard events for accessibility
   * Close on Escape key, trap focus within modal
   */
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }

      // Focus trap: keep focus within modal
      if (event.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements && focusableElements.length > 0) {
          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];

          if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          } else if (!event.shiftKey && document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    // Set initial focus to close button
    closeButtonRef.current?.focus();

    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [onClose]);

  /**
   * Handle click outside modal to close
   */
  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          ref={closeButtonRef}
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 rounded-full p-1 min-w-[44px] min-h-[44px] flex items-center justify-center"
          aria-label="Close attendance details"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>

        {/* Modal content */}
        <div className="mt-2">
          <h3 id="modal-title" className="text-2xl font-bold text-gray-900 mb-6">
            Attendance Details
          </h3>

          <div className="space-y-4">
            {/* Date */}
            <div className="border-b border-gray-200 pb-3">
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Date</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{formatDate(date)}</p>
            </div>

            {/* Timestamp */}
            <div className="border-b border-gray-200 pb-3">
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Time</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{timestamp}</p>
            </div>

            {/* Station */}
            <div className="pb-3">
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Station</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{station}</p>
            </div>
          </div>

          {/* Action button */}
          <div className="mt-6">
            <button
              onClick={onClose}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-medium py-3 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors min-h-[44px]"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AttendanceDetails;
