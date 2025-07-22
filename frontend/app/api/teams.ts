import apiClient from './config';
import type { Team, TeamCreate, TeamUpdate } from './types';

export class TeamService {
  // Get all teams
  static async getTeams(): Promise<Team[]> {
    const response = await apiClient.get<Team[]>('/teams/');
    return response.data;
  }

  // Get team by ID
  static async getTeam(teamId: number): Promise<Team> {
    const response = await apiClient.get<Team>(`/teams/${teamId}`);
    return response.data;
  }

  // Get teams by guild ID
  static async getTeamsByGuild(guildId: number): Promise<Team[]> {
    const response = await apiClient.get<Team[]>(`/teams/guild/${guildId}`);
    return response.data;
  }

  // Create new team
  static async createTeam(teamData: TeamCreate): Promise<Team> {
    const response = await apiClient.post<Team>('/teams/', teamData);
    return response.data;
  }

  // Update team
  static async updateTeam(teamId: number, teamData: TeamUpdate): Promise<Team> {
    const response = await apiClient.put<Team>(`/teams/${teamId}`, teamData);
    return response.data;
  }

  // Delete team
  static async deleteTeam(teamId: number): Promise<void> {
    await apiClient.delete(`/teams/${teamId}`);
  }
} 