import { 
  authAPI, 
  businessInterestAPI, 
  sourcesAPI, 
  newsAPI, 
  analysisAPI 
} from '../../services/api';

// Mock axios at the module level
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: jest.fn(),
    get: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  })),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};
global.localStorage = localStorageMock;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('authAPI', () => {
    test('login calls auth endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { data: { access_token: 'test-token' } };
      mockAxios.create().post.mockResolvedValue(mockResponse);

      await authAPI.login();

      expect(mockAxios.create().post).toHaveBeenCalledWith('/auth/login');
    });

    test('getCurrentUser calls me endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { data: { client_id: 'testuser' } };
      mockAxios.create().get.mockResolvedValue(mockResponse);

      await authAPI.getCurrentUser();

      expect(mockAxios.create().get).toHaveBeenCalledWith('/auth/me');
    });
  });

  describe('businessInterestAPI', () => {
    test('create calls business interest endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { data: { id: 1, interest_text: 'Technology' } };
      mockAxios.create().post.mockResolvedValue(mockResponse);

      await businessInterestAPI.create({ interest_text: 'Technology' });

      expect(mockAxios.create().post).toHaveBeenCalledWith('/analysis/business-interest', {
        interest_text: 'Technology',
      });
    });

    test('getAll calls business interests endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { data: [{ id: 1, interest_text: 'Technology' }] };
      mockAxios.create().get.mockResolvedValue(mockResponse);

      await businessInterestAPI.getAll();

      expect(mockAxios.create().get).toHaveBeenCalledWith('/analysis/business-interest');
    });
  });

  describe('sourcesAPI', () => {
    test('getAll calls sources endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { 
        data: { 
          sources: [{ source_id: 1, source_uel: 'https://example.com' }],
          total_count: 1
        } 
      };
      mockAxios.create().get.mockResolvedValue(mockResponse);

      await sourcesAPI.getAll();

      expect(mockAxios.create().get).toHaveBeenCalledWith('/sources/');
    });

    test('add calls add source endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { data: { source_id: 1, source_uel: 'https://example.com' } };
      mockAxios.create().post.mockResolvedValue(mockResponse);

      await sourcesAPI.add({ source_url: 'https://example.com' });

      expect(mockAxios.create().post).toHaveBeenCalledWith('/sources/', {
        source_url: 'https://example.com',
      });
    });

    test('remove calls remove source endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { data: { message: 'Source removed successfully' } };
      mockAxios.create().delete.mockResolvedValue(mockResponse);

      await sourcesAPI.remove(1);

      expect(mockAxios.create().delete).toHaveBeenCalledWith('/sources/1');
    });
  });

  describe('newsAPI', () => {
    test('analyze calls news analyze endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { data: { session_id: 1 } };
      mockAxios.create().post.mockResolvedValue(mockResponse);

      await newsAPI.analyze({
        sources: ['https://example.com'],
        business_interest: 'Technology',
      });

      expect(mockAxios.create().post).toHaveBeenCalledWith('/news/analyze', {
        sources: ['https://example.com'],
        business_interest: 'Technology',
      });
    });

    test('getSession calls session endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { 
        data: { 
          articles: [{ title: 'Test Article', content: 'Test content', url: 'https://example.com', source: 'Test Source' }],
          summary: 'Test summary'
        } 
      };
      mockAxios.create().get.mockResolvedValue(mockResponse);

      await newsAPI.getSession(1);

      expect(mockAxios.create().get).toHaveBeenCalledWith('/news/sessions/1');
    });
  });

  describe('analysisAPI', () => {
    test('getDashboard calls dashboard endpoint', async () => {
      const mockAxios = require('axios');
      const mockResponse = { 
        data: { 
          recent_sessions: [],
          recent_interests: []
        } 
      };
      mockAxios.create().get.mockResolvedValue(mockResponse);

      await analysisAPI.getDashboard();

      expect(mockAxios.create().get).toHaveBeenCalledWith('/analysis/dashboard');
    });
  });
}); 