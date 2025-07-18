import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Environment token for development/testing
const ENV_TOKEN = import.meta.env.VITE_AUTH_TOKEN;

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Check if we're in a browser environment before accessing localStorage
    const token = typeof window !== 'undefined' 
      ? localStorage.getItem('auth_token') || ENV_TOKEN
      : ENV_TOKEN;
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add context headers for better backend logging
    if (typeof window !== 'undefined') {
      // Add User-Agent to identify frontend requests
      config.headers['User-Agent'] = 'GuildRoster-Frontend';
      
      // Add Referer to show which page made the request
      config.headers['Referer'] = window.location.href;
      
      // Add custom header for additional context
      config.headers['X-Frontend-Route'] = window.location.pathname;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401) {
      // Only access localStorage and window in browser environment
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        // Redirect to login page
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient; 