import apiClient from './config';
import type { Invite, InviteCreate, InviteListResponse } from './types';

export class InviteService {
  /**
   * Generate a new invite code (superuser only)
   */
  static async createInvite(data: InviteCreate = {}): Promise<Invite> {
    try {
      const response = await apiClient.post<Invite>('/invites/', data);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 403) {
        throw new Error('Only superusers can generate invite codes');
      } else if (error.response?.status === 422) {
        throw new Error('Invalid input data');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Failed to generate invite code. Please try again.');
      }
    }
  }

  /**
   * Get all invite codes created by the current user
   */
  static async getInvites(skip: number = 0, limit: number = 100): Promise<InviteListResponse> {
    try {
      const response = await apiClient.get<InviteListResponse>('/invites/', {
        params: { skip, limit }
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Authentication required');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Failed to fetch invite codes. Please try again.');
      }
    }
  }

  /**
   * Get a specific invite code by ID
   */
  static async getInvite(inviteId: number): Promise<Invite> {
    try {
      const response = await apiClient.get<Invite>(`/invites/${inviteId}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Invite code not found');
      } else if (error.response?.status === 401) {
        throw new Error('Authentication required');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Failed to fetch invite code. Please try again.');
      }
    }
  }

  /**
   * Invalidate an unused invite code
   */
  static async invalidateInvite(inviteId: number): Promise<void> {
    try {
      await apiClient.delete(`/invites/${inviteId}`);
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Invite code not found');
      } else if (error.response?.status === 400) {
        throw new Error(error.response.data.detail || 'Cannot invalidate this invite code');
      } else if (error.response?.status === 401) {
        throw new Error('Authentication required');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Failed to invalidate invite code. Please try again.');
      }
    }
  }

  /**
   * Register a new user with an invite code
   */
  static async registerUser(userData: {
    username: string;
    password: string;
    invite_code: string;
  }): Promise<any> {
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
} 