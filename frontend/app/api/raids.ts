import apiClient from './config';
import type { Raid, RaidCreate, RaidUpdate } from './types';

export class RaidService {
  // Get all raids
  static async getRaids(): Promise<Raid[]> {
    const response = await apiClient.get<Raid[]>('/raids/');
    return response.data;
  }

  // Get raid by ID
  static async getRaid(raidId: number): Promise<Raid> {
    const response = await apiClient.get<Raid>(`/raids/${raidId}`);
    return response.data;
  }

  // Get raids by team ID
  static async getRaidsByTeam(teamId: number): Promise<Raid[]> {
    const response = await apiClient.get<Raid[]>(`/raids/team/${teamId}`);
    return response.data;
  }

  // Get raids by scenario ID
  static async getRaidsByScenario(scenarioId: number): Promise<Raid[]> {
    const response = await apiClient.get<Raid[]>(`/raids/scenario/${scenarioId}`);
    return response.data;
  }

  // Create new raid
  static async createRaid(raidData: RaidCreate): Promise<Raid> {
    const response = await apiClient.post<Raid>('/raids/', raidData);
    return response.data;
  }

  // Update raid
  static async updateRaid(raidId: number, raidData: RaidUpdate): Promise<Raid> {
    const response = await apiClient.put<Raid>(`/raids/${raidId}`, raidData);
    return response.data;
  }

  // Delete raid
  static async deleteRaid(raidId: number): Promise<void> {
    await apiClient.delete(`/raids/${raidId}`);
  }
} 