// /src/frontend/services/speechService.js
import { api, ASR_SERVICE_URL, TTS_SERVICE_URL } from './api';

export const transcribeAudio = async (audioBlob, options = {}) => {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.wav');
  
  try {
    const response = await api.post(`${ASR_SERVICE_URL}/transcribe`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: {
        language: options.language || 'en-US',
        punctuation: options.punctuation !== false,
        profanity_filter: !!options.profanityFilter
      }
    });
    return response.data;
  } catch (error) {
    console.error('Transcription error:', error);
    throw error;
  }
};

export const synthesizeSpeech = async (text, options = {}) => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('language', options.language || 'en-US');
  formData.append('voice', options.voice || 'female-1');
  formData.append('speaking_rate', options.speakingRate || 1.0);
  formData.append('pitch', options.pitch || 0.0);
  
  try {
    const response = await api.post(`${TTS_SERVICE_URL}/synthesize`, formData);
    return response.data;
  } catch (error) {
    console.error('Speech synthesis error:', error);
    throw error;
  }
};