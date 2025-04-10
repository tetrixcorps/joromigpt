// /src/frontend/components/speech/TextToSpeech.jsx
import React, { useState } from 'react';
import useSpeechSynthesis from '../../hooks/useSpeechSynthesis';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import { useLanguage } from '../../context/LanguageContext';
import './TextToSpeech.css';

const TextToSpeech = ({ text }) => {
  const { isSpeaking, error, speak, stop } = useSpeechSynthesis();
  const [isLoading, setIsLoading] = useState(false);
  const { language, voice } = useLanguage();
  
  const handleSpeak = async () => {
    if (isSpeaking) {
      stop();
      return;
    }
    
    if (!text) return;
    
    try {
      setIsLoading(true);
      await speak(text, { language, voice });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="text-to-speech">
      <Button 
        onClick={handleSpeak}
        disabled={!text || isLoading}
        className={isSpeaking ? 'speaking' : ''}
      >
        {isLoading ? <LoadingSpinner size="small" /> : isSpeaking ? 'Stop' : 'Speak'}
      </Button>
      
      {error && <ErrorMessage message={error} />}
    </div>
  );
};

export default TextToSpeech;