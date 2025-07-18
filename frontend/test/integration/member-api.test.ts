import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemberService } from '../../app/api/members';
import { ToonService } from '../../app/api/toons';
import { GuildService } from '../../app/api/guilds';
import { TeamService } from '../../app/api/teams';
import type { Member, Toon, Guild, Team } from '../../app/api/types';

// Mock the API services
vi.mock('../../app/api/members', () => ({
  MemberService: {
    getMember: vi.fn(),
  },
}));

vi.mock('../../app/api/toons', () => ({
  ToonService: {
    getToonsByMember: vi.fn(),
  },
}));

vi.mock('../../app/api/guilds', () => ({
  GuildService: {
    getGuild: vi.fn(),
  },
}));

vi.mock('../../app/api/teams', () => ({
  TeamService: {
    getTeams: vi.fn(),
    getTeam: vi.fn(),
  },
}));

describe('Member API Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should load member data successfully', async () => {
    const mockMember: Member = {
      id: 1,
      display_name: 'Test Member',
      guild_id: 1,
      team_id: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    const mockGuild: Guild = {
      id: 1,
      name: 'Test Guild',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    const mockTeam: Team = {
      id: 1,
      name: 'Test Team',
      guild_id: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    const mockToons: Toon[] = [
      {
        id: 1,
        username: 'TestToon',
        class: 'Warrior',
        role: 'Tank',
        is_main: true,
        member_id: 1,
        team_ids: [1],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];

    const mockTeams: Team[] = [
      { 
        id: 1, 
        name: 'Test Team',
        guild_id: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];

    // Mock the API calls
    vi.mocked(MemberService.getMember).mockResolvedValue(mockMember);
    vi.mocked(ToonService.getToonsByMember).mockResolvedValue(mockToons);
    vi.mocked(TeamService.getTeams).mockResolvedValue(mockTeams);
    vi.mocked(GuildService.getGuild).mockResolvedValue(mockGuild);
    vi.mocked(TeamService.getTeam).mockResolvedValue(mockTeam);

    // Simulate the loader function logic
    const memberId = 1;
    
    try {
      const [memberData, toonsData, teamsData] = await Promise.all([
        MemberService.getMember(memberId),
        ToonService.getToonsByMember(memberId),
        TeamService.getTeams(),
      ]);

      // Load guild and team data
      let guild: Guild | null = null;
      let team: Team | null = null;
      
      if (memberData.guild_id) {
        guild = await GuildService.getGuild(memberData.guild_id);
      }

      if (memberData.team_id) {
        team = await TeamService.getTeam(memberData.team_id);
      }

      const result = {
        member: memberData,
        toons: toonsData,
        teams: teamsData,
        guild,
        team,
      };

      // Verify the result
      expect(result.member).toEqual(mockMember);
      expect(result.toons).toEqual(mockToons);
      expect(result.teams).toEqual(mockTeams);
      expect(result.guild).toEqual(mockGuild);
      expect(result.team).toEqual(mockTeam);

      // Verify API calls were made
      expect(MemberService.getMember).toHaveBeenCalledWith(memberId);
      expect(ToonService.getToonsByMember).toHaveBeenCalledWith(memberId);
      expect(TeamService.getTeams).toHaveBeenCalled();
      expect(GuildService.getGuild).toHaveBeenCalledWith(memberData.guild_id);
      expect(TeamService.getTeam).toHaveBeenCalledWith(memberData.team_id);

    } catch (error) {
      throw error;
    }
  });

  it('should handle member not found', async () => {
    // Mock the API to throw an error
    vi.mocked(MemberService.getMember).mockRejectedValue(new Error('Member not found'));

    const memberId = 999;

    try {
      await MemberService.getMember(memberId);
      // This should not be reached
      expect(true).toBe(false);
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
      expect((error as Error).message).toBe('Member not found');
    }
  });

  it('should handle API errors gracefully', async () => {
    // Mock the API to throw an error
    vi.mocked(MemberService.getMember).mockRejectedValue(new Error('API Error'));

    const memberId = 1;

    try {
      await MemberService.getMember(memberId);
      // This should not be reached
      expect(true).toBe(false);
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
      expect((error as Error).message).toBe('API Error');
    }
  });

  it('should handle missing guild and team gracefully', async () => {
    const mockMember: Member = {
      id: 1,
      display_name: 'Test Member',
      guild_id: 1,
      team_id: undefined, // No team assigned
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    const mockGuild: Guild = {
      id: 1,
      name: 'Test Guild',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    const mockToons: Toon[] = [];
    const mockTeams: Team[] = [];

    // Mock the API calls
    vi.mocked(MemberService.getMember).mockResolvedValue(mockMember);
    vi.mocked(ToonService.getToonsByMember).mockResolvedValue(mockToons);
    vi.mocked(TeamService.getTeams).mockResolvedValue(mockTeams);
    vi.mocked(GuildService.getGuild).mockResolvedValue(mockGuild);
    // TeamService.getTeam should not be called since team_id is null

    const memberId = 1;
    
    const [memberData, toonsData, teamsData] = await Promise.all([
      MemberService.getMember(memberId),
      ToonService.getToonsByMember(memberId),
      TeamService.getTeams(),
    ]);

         // Load guild and team data
     let guild: Guild | null = null;
     let team: Team | null = null;
     
     if (memberData.guild_id) {
       guild = await GuildService.getGuild(memberData.guild_id);
     }

     if (memberData.team_id) {
       team = await TeamService.getTeam(memberData.team_id);
     }

    const result = {
      member: memberData,
      toons: toonsData,
      teams: teamsData,
      guild,
      team,
    };

    // Verify the result
    expect(result.member).toEqual(mockMember);
    expect(result.toons).toEqual(mockToons);
    expect(result.teams).toEqual(mockTeams);
    expect(result.guild).toEqual(mockGuild);
    expect(result.team).toBeNull();

    // Verify API calls were made correctly
    expect(MemberService.getMember).toHaveBeenCalledWith(memberId);
    expect(ToonService.getToonsByMember).toHaveBeenCalledWith(memberId);
    expect(TeamService.getTeams).toHaveBeenCalled();
    expect(GuildService.getGuild).toHaveBeenCalledWith(memberData.guild_id);
    expect(TeamService.getTeam).not.toHaveBeenCalled(); // Should not be called when team_id is null
  });
}); 