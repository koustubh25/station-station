/**
 * ErrorMessage Component
 *
 * Displays user-friendly error messages with an optional retry button.
 * Includes accessible error announcement for screen readers.
 *
 * @param {Object} props - Component props
 * @param {string} props.message - User-friendly error message to display
 * @param {Function} [props.onRetry] - Optional callback function for retry action
 * @returns {JSX.Element} ErrorMessage component
 */
function ErrorMessage({ message, onRetry }) {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[400px] px-4"
      role="alert"
      aria-live="assertive"
    >
      {/* Error Icon */}
      <div
        className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mb-4"
        aria-hidden="true"
      >
        <svg
          className="w-8 h-8 text-red-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      {/* Error Message */}
      <h2 className="text-xl font-semibold text-gray-800 mb-2 text-center">
        Oops! Something went wrong
      </h2>
      <p className="text-base text-gray-600 mb-6 text-center max-w-md">
        {message}
      </p>

      {/* Retry Button (conditional) */}
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-6 py-3 bg-attended text-white font-medium rounded-md
                     hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-attended
                     focus:ring-offset-2 transition-colors min-h-[44px] min-w-[100px]"
          aria-label="Retry loading attendance data"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

export default ErrorMessage;
