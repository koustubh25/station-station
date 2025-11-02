/**
 * UserSelector Component
 *
 * A dropdown selector for choosing a user from the attendance data.
 * Always visible regardless of the number of users.
 *
 * @param {Object} props - Component props
 * @param {string[]} props.users - Array of usernames to display in the dropdown
 * @param {string} props.selectedUser - Currently selected username
 * @param {Function} props.onUserChange - Callback function called when user selection changes
 * @returns {JSX.Element} UserSelector component
 */
function UserSelector({ users, selectedUser, onUserChange }) {
  const handleChange = (event) => {
    onUserChange(event.target.value);
  };

  return (
    <div className="w-full">
      <label
        htmlFor="user-selector"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Select User
      </label>
      <select
        id="user-selector"
        value={selectedUser}
        onChange={handleChange}
        className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm
                   focus:outline-none focus:ring-2 focus:ring-attended focus:border-attended
                   text-base bg-white cursor-pointer
                   hover:border-gray-400 transition-colors"
        aria-label="Select user to view attendance"
      >
        {users.map((user) => (
          <option key={user} value={user}>
            {user}
          </option>
        ))}
      </select>
    </div>
  );
}

export default UserSelector;
