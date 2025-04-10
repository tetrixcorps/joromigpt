// /src/frontend/hooks/useSpeechSynthesis.js
import { useState, useRef } from 'react';
import { synthesizeSpeech } from '../services/speechService';

export default function useSpeechSynthesis() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState(null);
  const audioRef = useRef(new Audio());
  
  const speak = async (text, options = {}) => {
    try {
      setError(null);
      
      // Stop any current speech
      if (isSpeaking) {
        audioRef.current.pause();
      }
      
      // Get audio from TTS service
      const response = await synthesizeSpeech(text, options);
      
      // Create audio from base64
      const audioSrc = `data:audio/wav;base64,${response.audio_base64}`;
      audioRef.current.src = audioSrc;
      
      // Set up event handlers
      audioRef.current.onplay = () => setIsSpeaking(true);
      audioRef.current.onended = () => setIsSpeaking(false);
      audioRef.current.onerror = (e) => {
        setError('Error playing audio');
        setIsSpeaking(false);
        console.error('Audio playback error:', e);
      };
      
      // Play the audio
      await audioRef.current.play();
      
      return response;
    } catch (err) {
      setError(err.message || 'Failed to synthesize speech');
      console.error('Speech synthesis error:', err);
      throw err;
    }
  };
  
  const stop = () => {
    if (isSpeaking) {
      audioRef.current.pause();
      setIsSpeaking(false);
    }
  };
  
  return {
    isSpeaking,
    error,
    speak,
    stop
  };
}