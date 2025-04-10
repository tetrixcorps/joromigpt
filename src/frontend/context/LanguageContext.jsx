// /src/frontend/context/LanguageContext.jsx
import React, { createContext, useState, useContext } from 'react';

const LanguageContext = createContext();

export const SUPPORTED_LANGUAGES = [
  { code: 'en-US', name: 'English (US)' },
  { code: 'fr-FR', name: 'French' },
  { code: 'es-ES', name: 'Spanish' },
  { code: 'sw-KE', name: 'Swahili' },
  { code: 'yo-NG', name: 'Yoruba' },
  { code: 'ha-NG', name: 'Hausa' },
  { code: 'zu-ZA', name: 'Zulu' },
  { code: 'xh-ZA', name: 'Xhosa' },
  { code: 'af-ZA', name: 'Afrikaans' }
];

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en-US');
  const [voice, setVoice] = useState('female-1');
  
  const value = {
    language,
    setLanguage,
    voice,
    setVoice,
    supportedLanguages: SUPPORTED_LANGUAGES
  };
  
  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};