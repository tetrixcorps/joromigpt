// /src/frontend/components/common/ErrorMessage.jsx
import React from 'react';
import './ErrorMessage.css';

const ErrorMessage = ({ message }) => {
  if (!message) return null;
  
  return (
    <div className="error-message">
      <span>{message}</span>
    </div>
  );
};

export default ErrorMessage;