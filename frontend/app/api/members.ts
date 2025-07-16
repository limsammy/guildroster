import apiClient from './config';
import type { Member, MemberCreate, MemberUpdate } from './types';

export class MemberService {
  // Get all members
  static async getMembers(): Promise<Member[]> {
    const response = await apiClient.get<Member[]>('/members/');
    return response.data;
  }

  // Get member by ID
  static async getMember(memberId: number): Promise<Member> {
    const response = await apiClient.get<Member>(`/members/${memberId}`);
    return response.data;
  }

  // Get members by guild ID
  static async getMembersByGuild(guildId: number): Promise<Member[]> {
    const response = await apiClient.get<Member[]>(`/members/guild/${guildId}`);
    return response.data;
  }

  // Get members by team ID
  static async getMembersByTeam(teamId: number): Promise<Member[]> {
    const response = await apiClient.get<Member[]>(`/members/team/${teamId}`);
    return response.data;
  }

  // Create new member
  static async createMember(memberData: MemberCreate): Promise<Member> {
    const response = await apiClient.post<Member>('/members/', memberData);
    return response.data;
  }

  // Update member
  static async updateMember(memberId: number, memberData: MemberUpdate): Promise<Member> {
    const response = await apiClient.put<Member>(`/members/${memberId}`, memberData);
    return response.data;
  }

  // Delete member
  static async deleteMember(memberId: number): Promise<void> {
    await apiClient.delete(`/members/${memberId}`);
  }
} 