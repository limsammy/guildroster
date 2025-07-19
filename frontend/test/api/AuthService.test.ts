import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import AuthService from '../../app/api/auth';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      post: vi.fn(),
      get: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
  },
}));

describe('AuthService', () => {
  let mockAxiosInstance: any;

  beforeEach(() => {
    vi.clearAllMocks();
    // Get the mocked axios instance
    const axios = require('axios');
    mockAxiosInstance = axios.default.create();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('login', () => {
    it('should login successfully and return user data', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user_id: 1,
          username: 'testuser',
          is_superuser: false,
        },
      };

      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const credentials = { username: 'testuser', password: 'password' };
      const result = await AuthService.login(credentials);

      expect(result).toEqual(mockResponse.data);
    });

    it('should handle login errors', async () => {
      const mockError = {
        response: {
          status: 401,
          data: { detail: 'Invalid credentials' },
        },
      };

      mockAxiosInstance.post.mockRejectedValue(mockError);

      const credentials = { username: 'testuser', password: 'wrongpassword' };

      await expect(AuthService.login(credentials)).rejects.toThrow(
        'Invalid username or password'
      );
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      const mockResponse = { data: { message: 'Logged out successfully' } };

      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      // Mock window.location
      const originalLocation = window.location;
      Object.defineProperty(window, 'location', {
        value: { href: '' },
        writable: true,
      });

      await AuthService.logout();

      expect(window.location.href).toBe('/');
      
      // Restore original location
      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true,
      });
    });

    it('should handle logout errors gracefully', async () => {
      const mockError = new Error('Network error');

      mockAxiosInstance.post.mockRejectedValue(mockError);

      // Mock window.location
      const originalLocation = window.location;
      Object.defineProperty(window, 'location', {
        value: { href: '' },
        writable: true,
      });

      // Mock console.warn
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      await AuthService.logout();

      expect(consoleSpy).toHaveBeenCalledWith('Logout request failed:', mockError);
      expect(window.location.href).toBe('/');
      
      // Restore
      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true,
      });
      consoleSpy.mockRestore();
    });
  });

  describe('getCurrentUser', () => {
    it('should return user info when authenticated', async () => {
      const mockUser = {
        user_id: 1,
        username: 'testuser',
        is_superuser: false,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockUser });

      const result = await AuthService.getCurrentUser();

      expect(result).toEqual(mockUser);
    });

    it('should return null when not authenticated', async () => {
      const mockError = { response: { status: 401 } };

      mockAxiosInstance.get.mockRejectedValue(mockError);

      const result = await AuthService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when user is authenticated', async () => {
      const mockUser = {
        user_id: 1,
        username: 'testuser',
        is_superuser: false,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockUser });

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false when user is not authenticated', async () => {
      const mockError = { response: { status: 401 } };

      mockAxiosInstance.get.mockRejectedValue(mockError);

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('getToken', () => {
    it('should return environment token when available', () => {
      // Mock environment variable
      const originalEnv = (import.meta as any).env.VITE_AUTH_TOKEN;
      (import.meta as any).env.VITE_AUTH_TOKEN = 'env-token';

      const result = AuthService.getToken();

      expect(result).toBe('env-token');
      
      // Restore
      (import.meta as any).env.VITE_AUTH_TOKEN = originalEnv;
    });

    it('should return null when no environment token', () => {
      // Mock environment variable
      const originalEnv = (import.meta as any).env.VITE_AUTH_TOKEN;
      (import.meta as any).env.VITE_AUTH_TOKEN = undefined;

      const result = AuthService.getToken();

      expect(result).toBeNull();
      
      // Restore
      (import.meta as any).env.VITE_AUTH_TOKEN = originalEnv;
    });
  });

  describe('validateSession', () => {
    it('should return true when session is valid', async () => {
      const mockUser = {
        user_id: 1,
        username: 'testuser',
        is_superuser: false,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockUser });

      const result = await AuthService.validateSession();

      expect(result).toBe(true);
    });

    it('should return false when session is invalid', async () => {
      const mockError = { response: { status: 401 } };

      mockAxiosInstance.get.mockRejectedValue(mockError);

      const result = await AuthService.validateSession();

      expect(result).toBe(false);
    });
  });
}); 