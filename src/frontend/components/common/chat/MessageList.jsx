// /src/frontend/components/chat/MessageList.jsx
import React from 'react';
import TextToSpeech from '../speech/TextToSpeech';
import './MessageList.css';

const MessageList = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div className="empty-message-list">
        <p>Start a conversation by sending a message or recording your voice.</p>
      </div>
    );
  }
  
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div 
          key={index} 
          className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
        >
          <div className="message-content">
            <p>{message.content}</p>
          </div>
          
          {message.role === 'assistant' && (
            <div className="message-actions">
              <TextToSpeech text={message.content} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default MessageList;