import apiClient from './config';
import type { Guild, GuildCreate, GuildUpdate, PaginatedResponse } from './types';

export class GuildService {
  // Get all guilds
  static async getGuilds(): Promise<Guild[]> {
    const response = await apiClient.get<Guild[]>('/guilds/');
    return response.data;
  }

  // Get guild by ID
  static async getGuild(guildId: number): Promise<Guild> {
    const response = await apiClient.get<Guild>(`/guilds/${guildId}`);
    return response.data;
  }

  // Create new guild
  static async createGuild(guildData: GuildCreate): Promise<Guild> {
    const response = await apiClient.post<Guild>('/guilds/', guildData);
    return response.data;
  }

  // Update guild
  static async updateGuild(guildId: number, guildData: GuildUpdate): Promise<Guild> {
    const response = await apiClient.put<Guild>(`/guilds/${guildId}`, guildData);
    return response.data;
  }

  // Delete guild
  static async deleteGuild(guildId: number): Promise<void> {
    await apiClient.delete(`/guilds/${guildId}`);
  }
} 