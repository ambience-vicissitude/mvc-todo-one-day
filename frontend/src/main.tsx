/** @file main.tsx
 * 
 * Entry point for the React application.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { logger } from './logger';
import './styles.css';

// Global error handling for uncaught errors and unhandled promise rejections.
window.addEventListener('error', (event) => logger.error(`uncaught: ${event.message}`));
window.addEventListener('unhandledrejection', (event) =>
  logger.error(`unhandled rejection: ${String(event.reason)}`),
);

// Render the main application component into the root element.
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
