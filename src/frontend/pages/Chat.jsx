// /src/frontend/pages/Chat.jsx
import React from 'react';
import ChatInterface from '../components/chat/ChatInterface';
import { useLanguage } from '../context/LanguageContext';
import './Chat.css';

const Chat = () => {
  const { language } = useLanguage();
  
  return (
    <div className="chat-page">
      <header className="chat-header">
        <h1>AI Assistant</h1>
        <p>Currently using: {language}</p>
      </header>
      
      <main className="chat-main">
        <ChatInterface />
      </main>
    </div>
  );
};

export default Chat;