import axios from 'axios';

// Function to get API base URL - makes testing easier
export const getApiBaseUrl = () => process.env.REACT_APP_API_BASE_URL || '';

// Get environment variables or use defaults
const API_BASE_URL = getApiBaseUrl();
const ASR_SERVICE_URL = `${API_BASE_URL}/asr`;
const TTS_SERVICE_URL = `${API_BASE_URL}/tts`;
const LLM_SERVICE_URL = `${API_BASE_URL}/llm`;

// Create axios instance for API calls
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export { api, ASR_SERVICE_URL, TTS_SERVICE_URL, LLM_SERVICE_URL };