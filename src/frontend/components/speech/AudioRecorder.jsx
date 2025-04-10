import React, { useState, useEffect } from 'react';
import useAudioRecording from '../../hooks/useAudioRecording';
import { transcribeAudio } from '../../services/speechService';
import { sendWhatsAppVoiceNote } from '../../services/whatsappService';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import { useLanguage } from '../../context/LanguageContext';
import './AudioRecorder.css';

const AudioRecorder = ({ onTranscriptionComplete, recipientId }) => {
  const { isRecording, audioBlob, error: recordingError, startRecording, stopRecording } = useAudioRecording();
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcriptionError, setTranscriptionError] = useState(null);
  const { language } = useLanguage();

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

          // Convert audioBlob to base64 for sending
          const reader = new FileReader();
          reader.onloadend = async () => {
            const base64Audio = reader.result.split(',')[1]; // Get base64 part
            await sendWhatsAppVoiceNote(recipientId, base64Audio);
          };
          reader.readAsDataURL(audioBlob);
        } catch (err) {
          setTranscriptionError(err.message || 'Transcription failed');
        } finally {
          setIsTranscribing(false);
        }
      }
    };
    
    processRecording();
  }, [audioBlob, isRecording, language, onTranscriptionComplete, recipientId]);

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div>
      <Button onClick={toggleRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </Button>
      {isTranscribing && <LoadingSpinner />}
      {transcriptionError && <ErrorMessage message={transcriptionError} />}
    </div>
  );
};

export default AudioRecorder; 