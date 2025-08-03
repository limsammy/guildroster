import apiClient from './config';

// Types for authentication
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  user_id: number;
  username: string;
  is_superuser: boolean;
}

export interface UserInfo {
  user_id: number;
  username: string;
  is_superuser: boolean;
}

export interface UserRegistration {
  username: string;
  password: string;
  invite_code: string;
}

export interface AuthError {
  message: string;
  status?: number;
}

export class AuthService {
  /**
   * Login with username and password
   */
  static async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>('/users/login', credentials);
      
      // Don't store user info in localStorage - rely on session cookies
      // The session cookie will be automatically sent with requests
      
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Invalid username or password');
      } else if (error.response?.status === 422) {
        throw new Error('Invalid input data');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Login failed. Please try again.');
      }
    }
  }

  /**
   * Logout current user
   */
  static async logout(): Promise<void> {
    try {
      await apiClient.post('/users/logout');
    } catch (error) {
      // Even if the logout request fails, clear any stored data
      console.warn('Logout request failed:', error);
    } finally {
      // Clear any stored user data (for cleanup)
      if (typeof window !== 'undefined') {
        localStorage.removeItem('user_info');
        localStorage.removeItem('selectedGuildId');
      }
      // Always redirect to home page
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
    }
  }

  /**
   * Get current user info from session
   */
  static async getCurrentUser(): Promise<UserInfo | null> {
    try {
      // Always get user info from the server via session cookie
      const response = await apiClient.get<UserInfo>('/users/me');
      return response.data;
    } catch (error: any) {
      // If the request fails with 401, user is not authenticated (normal state)
      // If it fails with other errors, log them but still return null
      if (error.response?.status !== 401) {
        console.warn('Unexpected error getting current user:', error);
      }
      return null;
    }
  }

  /**
   * Check if user is authenticated by attempting to get user info
   */
  static async isAuthenticated(): Promise<boolean> {
    try {
      const user = await this.getCurrentUser();
      return user !== null;
    } catch (error) {
      return false;
    }
  }

  /**
   * Register a new user with an invite code
   */
  static async register(userData: UserRegistration): Promise<any> {
    try {
      const response = await apiClient.post('/users/register', userData);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail || 'Registration failed');
      } else if (error.response?.status === 404) {
        throw new Error('Invalid invite code');
      } else if (error.response?.status === 422) {
        throw new Error('Invalid input data');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Registration failed. Please try again.');
      }
    }
  }

  /**
   * Get auth token (only for API tokens, not user sessions)
   */
  static getToken(): string | null {
    return import.meta.env.VITE_AUTH_TOKEN || null;
  }

  /**
   * Validate session with backend
   */
  static async validateSession(): Promise<boolean> {
    try {
      await apiClient.get('/users/me');
      return true;
    } catch (error) {
      return false;
    }
  }
}

export default AuthService; 