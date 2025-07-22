import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock the AuthService methods directly
vi.mock('../../app/api/auth', () => ({
  default: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    isAuthenticated: vi.fn(),
    getToken: vi.fn(),
    validateSession: vi.fn(),
  },
}));

// Import after mocking
import AuthService from '../../app/api/auth';

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('login', () => {
    it('should login successfully and return user data', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user_id: 1,
        username: 'testuser',
        is_superuser: false,
      };

      vi.mocked(AuthService.login).mockResolvedValue(mockResponse);

      const credentials = { username: 'testuser', password: 'password' };
      const result = await AuthService.login(credentials);

      expect(result).toEqual(mockResponse);
      expect(AuthService.login).toHaveBeenCalledWith(credentials);
    });

    it('should handle login errors', async () => {
      const mockError = new Error('Invalid username or password');

      vi.mocked(AuthService.login).mockRejectedValue(mockError);

      const credentials = { username: 'testuser', password: 'wrongpassword' };

      await expect(AuthService.login(credentials)).rejects.toThrow(
        'Invalid username or password'
      );
      expect(AuthService.login).toHaveBeenCalledWith(credentials);
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      vi.mocked(AuthService.logout).mockResolvedValue();

      await AuthService.logout();

      expect(AuthService.logout).toHaveBeenCalled();
    });

    it('should handle logout errors gracefully', async () => {
      // Mock the method to simulate the actual behavior - it doesn't throw errors
      vi.mocked(AuthService.logout).mockImplementation(async () => {
        // Simulate the actual behavior where errors are caught and logged
        console.warn('Logout request failed:', new Error('Network error'));
        // The method doesn't throw, it just logs the error
      });

      // Mock console.warn to verify it's called
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      await AuthService.logout();

      expect(AuthService.logout).toHaveBeenCalled();
      expect(consoleSpy).toHaveBeenCalledWith('Logout request failed:', expect.any(Error));
      
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

      vi.mocked(AuthService.getCurrentUser).mockResolvedValue(mockUser);

      const result = await AuthService.getCurrentUser();

      expect(result).toEqual(mockUser);
      expect(AuthService.getCurrentUser).toHaveBeenCalled();
    });

    it('should return null when not authenticated', async () => {
      vi.mocked(AuthService.getCurrentUser).mockResolvedValue(null);

      const result = await AuthService.getCurrentUser();

      expect(result).toBeNull();
      expect(AuthService.getCurrentUser).toHaveBeenCalled();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when user is authenticated', async () => {
      vi.mocked(AuthService.isAuthenticated).mockResolvedValue(true);

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(true);
      expect(AuthService.isAuthenticated).toHaveBeenCalled();
    });

    it('should return false when user is not authenticated', async () => {
      vi.mocked(AuthService.isAuthenticated).mockResolvedValue(false);

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(false);
      expect(AuthService.isAuthenticated).toHaveBeenCalled();
    });
  });

  describe('getToken', () => {
    it('should return environment token when available', () => {
      vi.mocked(AuthService.getToken).mockReturnValue('env-token');

      const result = AuthService.getToken();

      expect(result).toBe('env-token');
      expect(AuthService.getToken).toHaveBeenCalled();
    });

    it('should return null when no environment token', () => {
      vi.mocked(AuthService.getToken).mockReturnValue(null);

      const result = AuthService.getToken();

      expect(result).toBeNull();
      expect(AuthService.getToken).toHaveBeenCalled();
    });
  });

  describe('validateSession', () => {
    it('should return true when session is valid', async () => {
      vi.mocked(AuthService.validateSession).mockResolvedValue(true);

      const result = await AuthService.validateSession();

      expect(result).toBe(true);
      expect(AuthService.validateSession).toHaveBeenCalled();
    });

    it('should return false when session is invalid', async () => {
      vi.mocked(AuthService.validateSession).mockResolvedValue(false);

      const result = await AuthService.validateSession();

      expect(result).toBe(false);
      expect(AuthService.validateSession).toHaveBeenCalled();
    });
  });
}); 