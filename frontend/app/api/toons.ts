import apiClient from './config';
import type { Toon, ToonCreate, ToonUpdate } from './types';

export class ToonService {
  // Get all toons
  static async getToons(): Promise<Toon[]> {
    const response = await apiClient.get<Toon[]>('/toons/');
    return response.data;
  }

  // Get toon by ID
  static async getToon(toonId: number): Promise<Toon> {
    const response = await apiClient.get<Toon>(`/toons/${toonId}`);
    return response.data;
  }



  // Create new toon
  static async createToon(toonData: ToonCreate): Promise<Toon> {
    const response = await apiClient.post<Toon>('/toons/', toonData);
    return response.data;
  }

  // Update toon
  static async updateToon(toonId: number, toonData: ToonUpdate): Promise<Toon> {
    const response = await apiClient.put<Toon>(`/toons/${toonId}`, toonData);
    return response.data;
  }

  // Delete toon
  static async deleteToon(toonId: number): Promise<void> {
    await apiClient.delete(`/toons/${toonId}`);
  }
} 