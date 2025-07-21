import axios from 'axios';

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
  withCredentials: true, // Enable cookies for both development and production
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Add API token only for system/admin endpoints (not user authentication)
    // This is for backend-to-backend communication, not user sessions
    if (ENV_TOKEN && config.url && (
      config.url.includes('/tokens/') || 
      config.url.includes('/admin/') ||
      config.url.includes('/system/')
    )) {
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