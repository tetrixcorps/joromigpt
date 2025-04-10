// /src/frontend/services/whatsappService.js
import { api } from './api';

// WhatsApp MCP server base URL - should come from env variable
const WHATSAPP_MCP_URL = process.env.REACT_APP_WHATSAPP_MCP_URL || 'http://localhost:3000';

// Check if user is authenticated with WhatsApp
export const checkWhatsAppAuth = async () => {
  try {
    const response = await fetch(`${WHATSAPP_MCP_URL}/auth/status`);
    const data = await response.json();
    return data.authenticated;
  } catch (error) {
    console.error('WhatsApp auth check error:', error);
    return false;
  }
};

// Get QR code URL for WhatsApp authentication
export const getWhatsAppQRCode = async () => {
  try {
    const response = await fetch(`${WHATSAPP_MCP_URL}/auth/qr`);
    const data = await response.json();
    return data.qrCodeUrl;
  } catch (error) {
    console.error('WhatsApp QR code fetch error:', error);
    throw error;
  }
};

// Search WhatsApp contacts
export const searchContacts = async (query) => {
  try {
    const response = await fetch(`${WHATSAPP_MCP_URL}/whatsapp/search_contacts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    const data = await response.json();
    return data.contacts;
  } catch (error) {
    console.error('WhatsApp contacts search error:', error);
    throw error;
  }
};

// Get recent chats
export const getRecentChats = async (limit = 20) => {
  try {
    const response = await fetch(`${WHATSAPP_MCP_URL}/whatsapp/list_chats`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ limit }),
    });
    const data = await response.json();
    return data.chats;
  } catch (error) {
    console.error('WhatsApp chats fetch error:', error);
    throw error;
  }
};

// Get messages from a specific chat
export const getChatMessages = async (chatId, limit = 50) => {
  try {
    const response = await fetch(`${WHATSAPP_MCP_URL}/whatsapp/list_messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        chat_id: chatId,
        limit
      }),
    });
    const data = await response.json();
    return data.messages;
  } catch (error) {
    console.error('WhatsApp messages fetch error:', error);
    throw error;
  }
};

// Send text message to WhatsApp
export const sendWhatsAppMessage = async (recipientId, message) => {
  try {
    const response = await fetch(`${WHATSAPP_MCP_URL}/whatsapp/send_message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        recipient: recipientId,
        message
      }),
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('WhatsApp message send error:', error);
    throw error;
  }
};

// Send voice note (as base64 audio) to WhatsApp
export const sendWhatsAppVoiceNote = async (recipientId, audioBase64) => {
  try {
    const response = await fetch(`${WHATSAPP_MCP_URL}/whatsapp/send_voice_note`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        recipient: recipientId,
        audio_data: audioBase64
      }),
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('WhatsApp voice note send error:', error);
    throw error;
  }
};