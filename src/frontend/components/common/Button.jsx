// /src/frontend/components/common/Button.jsx
import React from 'react';
import './Button.css';

const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  type = 'button', 
  className = '', 
  ...props 
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`button ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;