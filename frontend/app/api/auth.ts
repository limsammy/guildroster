import axios from 'axios';

// Types for authentication
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
  is_superuser: boolean;
}

export interface UserInfo {
  user_id: number;
  username: string;
  is_superuser: boolean;
}

export interface AuthError {
  message: string;
  status?: number;
}

// API base URL - adjust this to match your backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Environment token for development/testing (only for API calls, not user sessions)
const ENV_TOKEN = import.meta.env.VITE_AUTH_TOKEN;

// Check if we're in development mode
const isDevelopment = import.meta.env.DEV;

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: !isDevelopment, // Only use cookies in production
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // In development, add the session token from localStorage for user endpoints
    if (isDevelopment) {
      const sessionToken = localStorage.getItem('session_token');
      if (sessionToken && config.url && config.url.includes('/users/')) {
        config.headers.Authorization = `Bearer ${sessionToken}`;
      }
    }
    
    // For all other endpoints (teams, members, guilds, etc.), use session token if available
    if (isDevelopment && config.url && !config.url.includes('/users/')) {
      const sessionToken = localStorage.getItem('session_token');
      if (sessionToken && config.headers && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${sessionToken}`;
      }
    }
    
    // Add API token for non-user endpoints (fallback for testing)
    if (ENV_TOKEN && config.url && !config.url.includes('/users/')) {
      if (config.headers && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${ENV_TOKEN}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Let individual components handle authentication errors
    // Don't automatically redirect - let the UI handle it gracefully
    return Promise.reject(error);
  }
);

export class AuthService {
  /**
   * Login with username and password
   */
  static async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>('/users/login', credentials);
      
      // In development, store the token in localStorage
      if (isDevelopment) {
        localStorage.setItem('session_token', response.data.access_token);
        localStorage.setItem('user_info', JSON.stringify({
          user_id: response.data.user_id,
          username: response.data.username,
          is_superuser: response.data.is_superuser,
        }));
      }
      
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
      // Even if the logout request fails, clear local storage
      console.warn('Logout request failed:', error);
    } finally {
      // Clear localStorage in development
      if (isDevelopment) {
        localStorage.removeItem('session_token');
        localStorage.removeItem('user_info');
      }
      // Always redirect to home page
      window.location.href = '/';
    }
  }

  /**
   * Get current user info from session
   */
  static async getCurrentUser(): Promise<UserInfo | null> {
    try {
      // In development, try to get user info from localStorage first
      if (isDevelopment) {
        const userInfo = localStorage.getItem('user_info');
        if (userInfo) {
          return JSON.parse(userInfo);
        }
      }
      
      // Fall back to API call
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
   * Get auth token (only for API tokens, not user sessions)
   */
  static getToken(): string | null {
    return ENV_TOKEN || null;
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