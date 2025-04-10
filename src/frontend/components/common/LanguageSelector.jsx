// /src/frontend/components/common/LanguageSelector.jsx
import React from 'react';
import { useLanguage, SUPPORTED_LANGUAGES } from '../../context/LanguageContext';
import './LanguageSelector.css';

const LanguageSelector = () => {
  const { language, setLanguage } = useLanguage();
  
  return (
    <div className="language-selector-component">
      <label htmlFor="language-select">Language:</label>
      <select 
        id="language-select"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
      >
        {SUPPORTED_LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;