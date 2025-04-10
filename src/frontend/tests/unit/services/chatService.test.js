// /src/frontend/tests/unit/services/chatService.test.js
import { generateResponse } from '../../../services/chatService';
import { api } from '../../../services/api';

// Mock the api module
jest.mock('../../../services/api', () => ({
  api: {
    post: jest.fn()
  },
  LLM_SERVICE_URL: '/llm'
}));

describe('chatService', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('generateResponse should call API with correct parameters', async () => {
    // Setup
    const mockResponse = {
      data: {
        response: 'This is a test response',
        model: 'test-model'
      }
    };
    api.post.mockResolvedValue(mockResponse);

    const messages = [
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: 'Hi there' },
      { role: 'user', content: 'How are you?' }
    ];

    const options = {
      maxTokens: 500,
      temperature: 0.5
    };

    // Execute
    const result = await generateResponse(messages, options);

    // Verify
    expect(api.post).toHaveBeenCalledWith('/llm/chat', {
      messages: [
        { role: 'user', content: 'Hello' },
        { role: 'assistant', content: 'Hi there' },
        { role: 'user', content: 'How are you?' }
      ],
      max_tokens: 500,
      temperature: 0.5
    });
    expect(result).toEqual(mockResponse.data);
  });

  test('generateResponse should use default options when not provided', async () => {
    // Setup
    const mockResponse = {
      data: {
        response: 'This is a test response',
        model: 'test-model'
      }
    };
    api.post.mockResolvedValue(mockResponse);

    const messages = [
      { role: 'user', content: 'Hello' }
    ];

    // Execute
    await generateResponse(messages);

    // Verify
    expect(api.post).toHaveBeenCalledWith('/llm/chat', {
      messages: [
        { role: 'user', content: 'Hello' }
      ],
      max_tokens: 1024,
      temperature: 0.7
    });
  });

  test('generateResponse should handle errors', async () => {
    // Setup
    const errorMessage = 'Network error';
    api.post.mockRejectedValue(new Error(errorMessage));

    const messages = [
      { role: 'user', content: 'Hello' }
    ];

    // Execute & Verify
    await expect(generateResponse(messages)).rejects.toThrow(errorMessage);
  });
});