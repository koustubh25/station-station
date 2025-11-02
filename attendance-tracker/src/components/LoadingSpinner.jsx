/**
 * LoadingSpinner Component
 *
 * Displays a centered loading spinner with an accessible loading message.
 * Used to indicate data is being fetched or processed.
 *
 * @returns {JSX.Element} LoadingSpinner component
 */
function LoadingSpinner() {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[400px]"
      role="status"
      aria-live="polite"
    >
      {/* CSS Spinner */}
      <div
        className="w-16 h-16 border-4 border-gray-200 border-t-attended rounded-full animate-spin"
        aria-hidden="true"
      ></div>

      {/* Accessible loading message */}
      <p className="mt-4 text-lg text-gray-600 font-medium">
        Loading attendance data...
      </p>
    </div>
  );
}

export default LoadingSpinner;
