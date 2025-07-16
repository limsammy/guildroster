import apiClient from './config';
import type { UserLogin, UserLoginResponse, User, Token, TokenCreate } from './types';

export class AuthService {
  // Login user and get access token
  static async login(credentials: UserLogin): Promise<UserLoginResponse> {
    const response = await apiClient.post<UserLoginResponse>('/users/login', credentials);
    const { access_token, ...userData } = response.data;
    
    // Store token in localStorage
    localStorage.setItem('auth_token', access_token);
    
    return response.data;
  }

  // Logout user
  static async logout(): Promise<void> {
    localStorage.removeItem('auth_token');
    // Could also call a logout endpoint if needed
  }

  // Get current user info
  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  }

  // Check if user is authenticated
  static isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  // Get stored token
  static getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  // Create new token (superuser only)
  static async createToken(tokenData: TokenCreate): Promise<Token> {
    const response = await apiClient.post<Token>('/tokens/', tokenData);
    return response.data;
  }

  // Get all tokens (superuser only)
  static async getTokens(): Promise<Token[]> {
    const response = await apiClient.get<Token[]>('/tokens/');
    return response.data;
  }

  // Delete token (superuser only)
  static async deleteToken(tokenId: number): Promise<void> {
    await apiClient.delete(`/tokens/${tokenId}`);
  }
} 