// /src/frontend/components/chat/MessageInput.jsx
import React, { useState } from 'react';
import AudioRecorder from '../speech/AudioRecorder';
import Button from '../common/Button';
import './MessageInput.css';

const MessageInput = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  const handleTranscription = (transcription) => {
    if (transcription) {
      setMessage(transcription);
    }
  };
  
  return (
    <div className="message-input-container">
      <form onSubmit={handleSubmit} className="message-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
          className="message-input"
        />
        <Button 
          type="submit" 
          disabled={!message.trim() || disabled}
          className="send-button"
        >
          Send
        </Button>
      </form>
      
      <div className="voice-input">
        <AudioRecorder onTranscriptionComplete={handleTranscription} />
      </div>
    </div>
  );
};

export default MessageInput;