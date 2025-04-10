// /src/frontend/components/chat/ChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { generateResponse } from '../../services/chatService';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = async (content) => {
    if (!content.trim()) return;
    
    // Add user message
    const userMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);
    
    // Generate response
    try {
      setIsLoading(true);
      setError(null);
      
      const allMessages = [...messages, userMessage];
      const response = await generateResponse(allMessages);
      
      // Extract assistant message from response
      const assistantMessage = {
        role: 'assistant',
        content: response.choices[0].message.content
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message || 'Failed to generate response');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="chat-interface">
      <MessageList messages={messages} />
      <div ref={messagesEndRef} />
      
      {isLoading && (
        <div className="loading-indicator">
          <LoadingSpinner />
          <span>AI is thinking...</span>
        </div>
      )}
      
      {error && <ErrorMessage message={error} />}
      
      <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatInterface;