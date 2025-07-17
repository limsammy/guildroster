import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock axios with hoisted mock
vi.mock('axios', () => {
  const mockAxiosInstance = {
    post: vi.fn(),
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  };

  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
    },
  };
});

// Import AuthService after mocking axios
import AuthService from '../../app/api/auth';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: '',
  },
  writable: true,
});

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('login', () => {
    it('should successfully login and store token', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user_id: 1,
          username: 'testuser',
          is_superuser: false,
        },
      };

      // Get the mocked axios instance
      const axios = await import('axios');
      const mockAxios = axios.default as any;
      mockAxios.create().post.mockResolvedValue(mockResponse);

      const credentials = { username: 'testuser', password: 'testpass' };
      const result = await AuthService.login(credentials);

      expect(result).toEqual(mockResponse.data);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'test-token');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user_info', JSON.stringify({
        user_id: 1,
        username: 'testuser',
        is_superuser: false,
      }));
    });

    it('should throw error on invalid credentials', async () => {
      // Get the mocked axios instance
      const axios = await import('axios');
      const mockAxios = axios.default as any;
      mockAxios.create().post.mockRejectedValue({
        response: { status: 401 },
      });

      const credentials = { username: 'wrong', password: 'wrong' };

      await expect(AuthService.login(credentials)).rejects.toThrow('Invalid username or password');
    });

    it('should throw error on validation failure', async () => {
      // Get the mocked axios instance
      const axios = await import('axios');
      const mockAxios = axios.default as any;
      mockAxios.create().post.mockRejectedValue({
        response: { status: 422 },
      });

      const credentials = { username: '', password: '' };

      await expect(AuthService.login(credentials)).rejects.toThrow('Invalid input data');
    });
  });

  describe('logout', () => {
    it('should clear localStorage and redirect', () => {
      AuthService.logout();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user_info');
      expect(window.location.href).toBe('/');
    });
  });

  describe('getCurrentUser', () => {
    it('should return user info from localStorage', () => {
      const userInfo = {
        user_id: 1,
        username: 'testuser',
        is_superuser: false,
      };
      localStorageMock.getItem.mockReturnValue(JSON.stringify(userInfo));

      const result = AuthService.getCurrentUser();

      expect(result).toEqual(userInfo);
    });

    it('should return null when no user info exists', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = AuthService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when token exists', () => {
      localStorageMock.getItem.mockReturnValue('test-token');

      const result = AuthService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false when no token exists', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = AuthService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('getToken', () => {
    it('should return token from localStorage', () => {
      localStorageMock.getItem.mockReturnValue('test-token');

      const result = AuthService.getToken();

      expect(result).toBe('test-token');
    });

    it('should return null when no token exists', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = AuthService.getToken();

      expect(result).toBeNull();
    });
  });
}); 