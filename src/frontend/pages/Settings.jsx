// /src/frontend/pages/Settings.jsx
import React from 'react';
import LanguageSelector from '../components/common/LanguageSelector';
import VoiceSelector from '../components/common/VoiceSelector';
import { useLanguage } from '../context/LanguageContext';
import './Settings.css';

const Settings = () => {
  const { language } = useLanguage();
  
  return (
    <div className="settings-page">
      <h1>Settings</h1>
      
      <div className="settings-section">
        <h2>Language & Voice</h2>
        <p>Current language: {language}</p>
        
        <div className="settings-options">
          <LanguageSelector />
          <VoiceSelector />
        </div>
      </div>
      
      <div className="settings-section">
        <h2>About</h2>
        <p>African Voice AI Platform is designed to provide speech recognition, text-to-speech, and AI assistant capabilities in multiple African languages.</p>
        <p>Version: 1.0.0</p>
      </div>
    </div>
  );
};

export default Settings;