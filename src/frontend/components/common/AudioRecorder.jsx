// /src/frontend/components/speech/AudioRecorder.jsx
import React, { useState, useEffect } from 'react';
import useAudioRecording from '../../hooks/useAudioRecording';
import { transcribeAudio } from '../../services/speechService';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import AudioVisualizer from '../common/AudioVisualizer';
import { useLanguage } from '../../context/LanguageContext';
import './AudioRecorder.css';

const AudioRecorder = ({ onTranscriptionComplete }) => {
  const { isRecording, audioBlob, error: recordingError, startRecording, stopRecording } = useAudioRecording();
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcriptionError, setTranscriptionError] = useState(null);
  const { language } = useLanguage();
  
  // Process recording when stopped
  useEffect(() => {
    const processRecording = async () => {
      if (audioBlob && !isRecording) {
        try {
          setIsTranscribing(true);
          setTranscriptionError(null);
          
          const result = await transcribeAudio(audioBlob, { language });
          
          if (onTranscriptionComplete) {
            onTranscriptionComplete(result.text);
          }
        } catch (err) {
          setTranscriptionError(err.message || 'Transcription failed');
        } finally {
          setIsTranscribing(false);
        }
      }
    };
    
    processRecording();
  }, [audioBlob, isRecording, language, onTranscriptionComplete]);
  
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };
  
  return (
    <div className="audio-recorder">
      <Button 
        onClick={toggleRecording}
        disabled={isTranscribing}
        className={`record-button ${isRecording ? 'recording' : ''}`}
      >
        {isRecording ? 'Stop' : 'Record'}
      </Button>
      
      {isRecording && <AudioVisualizer />}
      
      {isTranscribing && (
        <div className="transcribing-indicator">
          <LoadingSpinner />
          <span>Transcribing...</span>
        </div>
      )}
      
      {recordingError && <ErrorMessage message={recordingError} />}
      {transcriptionError && <ErrorMessage message={transcriptionError} />}
    </div>
  );
};

export default AudioRecorder;