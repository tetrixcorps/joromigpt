// /src/frontend/components/common/VoiceSelector.jsx
import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import './VoiceSelector.css';

const VOICE_OPTIONS = [
  { id: 'female-1', name: 'Female 1' },
  { id: 'female-2', name: 'Female 2' },
  { id: 'male-1', name: 'Male 1' },
  { id: 'male-2', name: 'Male 2' }
];

const VoiceSelector = () => {
  const { voice, setVoice } = useLanguage();
  
  return (
    <div className="voice-selector">
      <label htmlFor="voice-select">Voice:</label>
      <select 
        id="voice-select"
        value={voice}
        onChange={(e) => setVoice(e.target.value)}
      >
        {VOICE_OPTIONS.map((voiceOption) => (
          <option key={voiceOption.id} value={voiceOption.id}>
            {voiceOption.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default VoiceSelector;