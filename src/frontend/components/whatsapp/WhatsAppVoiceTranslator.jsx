// /src/frontend/components/whatsapp/WhatsAppVoiceTranslator.jsx
import React, { useState, useRef } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { searchContacts } from '../../services/whatsappService';
import { processAndSendWhatsAppVoiceMessage } from '../../services/speechWhatsappService';
import useAudioRecording from '../../hooks/useAudioRecording';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import './WhatsAppVoiceTranslator.css';

const WhatsAppVoiceTranslator = () => {
  const { language } = useLanguage();
  const [contactSearch, setContactSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [sourceLanguage, setSourceLanguage] = useState(language || 'en-US');
  const [targetLanguage, setTargetLanguage] = useState('fr-FR');
  const [sendAudio, setSendAudio] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [transcribedText, setTranscribedText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  
  const { 
    isRecording, 
    audioBlob, 
    error: recordingError, 
    startRecording, 
    stopRecording 
  } = useAudioRecording();
  
  const searchTimeoutRef = useRef(null);
  
  const handleSearchChange = (e) => {
    const query = e.target.value;
    setContactSearch(query);
    
    // Debounce search
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (query.length > 2) {
      searchTimeoutRef.current = setTimeout(() => {
        handleSearch(query);
      }, 500);
    } else {
      setSearchResults([]);
    }
  };
  
  const handleSearch = async (query) => {
    try {
      setIsSearching(true);
      setError(null);
      const contacts = await searchContacts(query);
      setSearchResults(contacts);
    } catch (err) {
      setError('Failed to search contacts. Please try again.');
      console.error('Contact search error:', err);
    } finally {
      setIsSearching(false);
    }
  };
  
  const selectContact = (contact) => {
    setSelectedContact(contact);
    setSearchResults([]);
    setContactSearch(contact.name || contact.number);
  };
  
  const handleSendVoiceMessage = async () => {
    if (!selectedContact || !audioBlob) return;
    
    try {
      setIsProcessing(true);
      setError(null);
      setSuccessMessage('');
      setTranscribedText('');
      setTranslatedText('');
      
      const result = await processAndSendWhatsAppVoiceMessage(
        selectedContact.jid,
        audioBlob,
        sourceLanguage,
        targetLanguage,
        sendAudio
      );
      
      setTranscribedText(result.original);
      setTranslatedText(result.translated);
      setSuccessMessage(`Message sent successfully to ${selectedContact.name || selectedContact.number}!`);
    } catch (err) {
      setError('Failed to send voice message. Please try again.');
      console.error('Send voice message error:', err);
    } finally {
      setIsProcessing(false);
    }
  };
  
  return (
    <div className="whatsapp-voice-translator">
      <div className="contact-search">
        <label htmlFor="contact-search">Search for a contact:</label>
        <input
          id="contact-search"
          type="text"
          value={contactSearch}
          onChange={handleSearchChange}
          placeholder="Enter name or number"
        />
        
        {isSearching && <LoadingSpinner size="small" />}
        
        {searchResults.length > 0 && (
          <ul className="contact-results">
            {searchResults.map((contact) => (
              <li 
                key={contact.jid} 
                className="contact-item"
                onClick={() => selectContact(contact)}
              >
                {contact.name || contact.number}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="language-selector">
        <div>
          <label htmlFor="source-language">From:</label>
          <select
            id="source-language"
            value={sourceLanguage}
            onChange={(e) => setSourceLanguage(e.target.value)}
          >
            <option value="en-US">English</option>
            <option value="fr-FR">French</option>
            <option value="es-ES">Spanish</option>
            <option value="sw-KE">Swahili</option>
            <option value="yo-NG">Yoruba</option>
            <option value="ha-NG">Hausa</option>
          </select>
        </div>
        
        <div>
          <label htmlFor="target-language">To:</label>
          <select
            id="target-language"
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
          >
            <option value="en-US">English</option>
            <option value="fr-FR">French</option>
            <option value="es-ES">Spanish</option>
            <option value="sw-KE">Swahili</option>
            <option value="yo-NG">Yoruba</option>
            <option value="ha-NG">Hausa</option>
          </select>
        </div>
      </div>
      
      <div className="audio-option">
        <input
          type="checkbox"
          id="send-audio"
          checked={sendAudio}
          onChange={(e) => setSendAudio(e.target.checked)}
        />
        <label htmlFor="send-audio">Send translated audio message</label>
      </div>
      
      <div className="recording-controls">
        <Button 
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!selectedContact || isProcessing}
          className={isRecording ? "stop-recording" : "start-recording"}
        >
          {isRecording ? "Stop Recording" : "Start Recording"}
        </Button>
        
        {audioBlob && !isRecording && (
          <div className="audio-preview">
            <audio controls src={URL.createObjectURL(audioBlob)} />
            <Button 
              onClick={handleSendVoiceMessage}
              disabled={isProcessing}
              className="send-button"
            >
              Translate & Send
            </Button>
          </div>
        )}
      </div>
      
      {isProcessing && <LoadingSpinner message="Processing and sending message..." />}
      
      {error && <ErrorMessage message={error} />}
      
      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}
      
      {transcribedText && (
        <div className="transcription-result">
          <h4>Original Text:</h4>
          <p>{transcribedText}</p>
        </div>
      )}
      
      {translatedText && (
        <div className="translation-result">
          <h4>Translated Text:</h4>
          <p>{translatedText}</p>
        </div>
      )}
    </div>
  );
};

export default WhatsAppVoiceTranslator;