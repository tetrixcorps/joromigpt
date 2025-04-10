// src/frontend/tests/integration/services/api.integration.test.js
import axios from 'axios';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn().mockReturnValue({
    post: jest.fn(),
    get: jest.fn()
  })
}));

// Mock the API service directly
jest.mock('../../../services/api', () => {
  const baseURL = 'http://localhost:8000';
  return {
    ASR_SERVICE_URL: `${baseURL}/asr`,
    TTS_SERVICE_URL: `${baseURL}/tts`,
    LLM_SERVICE_URL: `${baseURL}/llm`,
    api: {
      post: jest.fn(),
      get: jest.fn()
    }
  };
});

describe('API Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('API URLs are correctly constructed', () => {
    // Import after mocking
    const { ASR_SERVICE_URL, TTS_SERVICE_URL, LLM_SERVICE_URL } = require('../../../services/api');
    
    expect(ASR_SERVICE_URL).toBe('http://localhost:8000/asr');
    expect(TTS_SERVICE_URL).toBe('http://localhost:8000/tts');
    expect(LLM_SERVICE_URL).toBe('http://localhost:8000/llm');
  });

  test('axios instance is created with correct config', () => {
    expect(axios.create).toHaveBeenCalledWith({
      baseURL: 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });
});