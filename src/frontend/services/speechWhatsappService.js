// /src/frontend/services/speechWhatsappService.js
import { api } from './api';
import { sendWhatsAppMessage, sendWhatsAppVoiceNote } from './whatsappService';

// Transcribe audio using ASR service
export const transcribeAudio = async (audioBlob, sourceLanguage = 'en-US') => {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.wav');
  
  try {
    const response = await api.post('/asr/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: {
        language: sourceLanguage,
        punctuation: true
      }
    });
    return response.data;
  } catch (error) {
    console.error('Audio transcription error:', error);
    throw error;
  }
};

// Translate text to another language using LLM service
export const translateText = async (text, sourceLanguage = 'en-US', targetLanguage = 'fr-FR') => {
  try {
    const response = await api.post('/llm/translate', {
      text,
      source_language: sourceLanguage,
      target_language: targetLanguage
    });
    return response.data.translatedText;
  } catch (error) {
    console.error('Translation error:', error);
    throw error;
  }
};

// Synthesize speech from text using TTS service
export const synthesizeSpeech = async (text, language = 'fr-FR') => {
  try {
    const response = await api.post('/tts/synthesize', {
      text,
      language
    }, {
      responseType: 'arraybuffer'
    });
    
    // Convert arraybuffer to base64
    const base64Audio = Buffer.from(response.data).toString('base64');
    return base64Audio;
  } catch (error) {
    console.error('Speech synthesis error:', error);
    throw error;
  }
};

// Process and send voice message with translation
export const processAndSendWhatsAppVoiceMessage = async (
  recipientId, 
  audioBlob, 
  sourceLanguage = 'en-US', 
  targetLanguage = 'fr-FR',
  sendTranslatedAudio = true
) => {
  try {
    // Step 1: Transcribe the original audio
    const transcriptionResult = await transcribeAudio(audioBlob, sourceLanguage);
    const transcribedText = transcriptionResult.text;
    
    // Step 2: Translate the transcribed text
    const translatedText = await translateText(transcribedText, sourceLanguage, targetLanguage);
    
    // Step 3: Send the translated text as a message
    await sendWhatsAppMessage(recipientId, translatedText);
    
    // Step 4 (Optional): Synthesize and send translated audio
    if (sendTranslatedAudio) {
      const translatedAudioBase64 = await synthesizeSpeech(translatedText, targetLanguage);
      await sendWhatsAppVoiceNote(recipientId, translatedAudioBase64);
    }
    
    return {
      success: true,
      original: transcribedText,
      translated: translatedText
    };
  } catch (error) {
    console.error('WhatsApp voice message processing error:', error);
    throw error;
  }
};