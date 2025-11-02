import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
// Import required CSS for external libraries
import 'react-calendar/dist/Calendar.css';
import 'react-datepicker/dist/react-datepicker.css';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
