import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// API Configuration
// Use API subdomain for production or fallback to environment variable
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://api.guildroster.io'  // API subdomain for production
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000');

// Log the API URL for debugging
console.log('API_BASE_URL:', API_BASE_URL);
console.log('Environment:', import.meta.env.MODE);

// Environment token for development/testing (only for API calls, not user sessions)
const ENV_TOKEN = import.meta.env.VITE_AUTH_TOKEN;

// Check if we're in development mode
const isDevelopment = import.meta.env.DEV;

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies for both development and production
});

// Request interceptor to add auth token for API calls
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
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

    // Add context headers for better backend logging
    if (typeof window !== 'undefined') {
      // Add User-Agent to identify frontend requests
      if (config.headers) {
        config.headers['User-Agent'] = 'GuildRoster-Frontend';
        
        // Add Referer to show which page made the request
        config.headers['Referer'] = window.location.href;
        
        // Add custom header for additional context
        config.headers['X-Frontend-Route'] = window.location.pathname;
      }
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
    // Let individual components handle authentication errors
    // Don't automatically redirect - let the UI handle it gracefully
    return Promise.reject(error);
  }
);

export default apiClient; 