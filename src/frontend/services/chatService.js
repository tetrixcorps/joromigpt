// /src/frontend/services/chatService.js
import { api, LLM_SERVICE_URL } from './api';

export const generateResponse = async (messages, options = {}) => {
  try {
    const response = await api.post(`${LLM_SERVICE_URL}/chat`, {
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      max_tokens: options.maxTokens || 1024,
      temperature: options.temperature || 0.7
    });
    return response.data;
  } catch (error) {
    console.error('LLM generation error:', error);
    throw error;
  }
};