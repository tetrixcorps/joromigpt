// /src/frontend/components/whatsapp/WhatsAppIntegration.jsx
import React, { useState } from 'react';
import WhatsAppAuth from './WhatsAppAuth';
import WhatsAppVoiceTranslator from './WhatsAppVoiceTranslator';
import './WhatsAppIntegration.css';

const WhatsAppIntegration = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <div className="whatsapp-integration-container">
      <h2>WhatsApp Voice Translator</h2>
      <p>Connect your WhatsApp account to send voice messages in different languages</p>
      
      {!isAuthenticated ? (
        <WhatsAppAuth onAuthSuccess={handleAuthSuccess} />
      ) : (
        <WhatsAppVoiceTranslator />
      )}
      
      <div className="whatsapp-info">
        <h3>How it works</h3>
        <ol>
          <li>Connect your WhatsApp account by scanning the QR code</li>
          <li>Search for a contact to message</li>
          <li>Record your voice message in your language</li>
          <li>Select the language you want to translate to</li>
          <li>Send the translated message to your contact</li>
        </ol>
        <p>Your WhatsApp data remains on your device and is only used when you explicitly send messages.</p>
      </div>
    </div>
  );
};

export default WhatsAppIntegration;