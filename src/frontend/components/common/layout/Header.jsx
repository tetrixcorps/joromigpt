// /src/frontend/components/layout/Header.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage, SUPPORTED_LANGUAGES } from '../../context/LanguageContext';
import './Header.css';

const Header = () => {
  const { language, setLanguage } = useLanguage();
  
  return (
    <header className="header">
      <div className="logo">
        <Link to="/">African Voice AI</Link>
      </div>
      
      <nav className="nav">
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/chat">Chat</Link></li>
          <li><Link to="/settings">Settings</Link></li>
        </ul>
      </nav>
      
      <div className="language-selector">
        <select 
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          aria-label="Select language"
        >
          {SUPPORTED_LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>
    </header>
  );
};

export default Header;