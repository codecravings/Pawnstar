import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Set dark mode based on localStorage or default to dark
const isDark = localStorage.getItem('darkMode') !== 'false';
if (isDark) {
  document.documentElement.classList.add('dark');
} else {
  document.documentElement.classList.remove('dark');
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);