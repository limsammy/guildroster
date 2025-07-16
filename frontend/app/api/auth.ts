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

export interface AuthError {
  message: string;
  status?: number;
}

// API base URL - adjust this to match your backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Environment token for development/testing
const ENV_TOKEN = import.meta.env.VITE_AUTH_TOKEN;

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token') || ENV_TOKEN;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
      window.location.href = '/login';
    }
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
      
      // Store token and user info
      localStorage.setItem('auth_token', response.data.access_token);
      localStorage.setItem('user_info', JSON.stringify({
        user_id: response.data.user_id,
        username: response.data.username,
        is_superuser: response.data.is_superuser,
      }));
      
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
  static logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    window.location.href = '/';
  }

  /**
   * Get current user info from localStorage
   */
  static getCurrentUser(): { user_id: number; username: string; is_superuser: boolean } | null {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    return !!(localStorage.getItem('auth_token') || ENV_TOKEN);
  }

  /**
   * Get auth token
   */
  static getToken(): string | null {
    return localStorage.getItem('auth_token') || ENV_TOKEN;
  }

  /**
   * Validate token with backend
   */
  static async validateToken(): Promise<boolean> {
    try {
      await apiClient.get('/'); // Health check endpoint
      return true;
    } catch (error) {
      return false;
    }
  }
}

export default AuthService; 