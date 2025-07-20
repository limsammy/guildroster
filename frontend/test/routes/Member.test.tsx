import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import MemberDetail, { loader } from '../../app/routes/member';
import { AuthProvider } from '../../app/contexts/AuthContext';

// Mock the API services
vi.mock('../../app/api/members', () => ({
  MemberService: {
    getMember: vi.fn(),
  },
}));

vi.mock('../../app/api/toons', () => ({
  ToonService: {
    getToonsByMember: vi.fn(),
    createToon: vi.fn(),
    updateToon: vi.fn(),
    deleteToon: vi.fn(),
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

vi.mock('../../app/api/auth', () => ({
  default: {
    isAuthenticated: vi.fn(() => true),
    getCurrentUser: vi.fn(() => ({ user_id: 1, username: 'testuser', is_superuser: true })),
    login: vi.fn(),
    logout: vi.fn(),
    validateToken: vi.fn(() => Promise.resolve(true)),
  },
  AuthService: {
    isAuthenticated: vi.fn(() => true),
    getCurrentUser: vi.fn(() => ({ user_id: 1, username: 'testuser', is_superuser: true })),
    login: vi.fn(),
    logout: vi.fn(),
    validateToken: vi.fn(() => Promise.resolve(true)),
  },
}));

// Import the mocked services
import { MemberService } from '../../app/api/members';
import { ToonService } from '../../app/api/toons';
import { GuildService } from '../../app/api/guilds';
import { TeamService } from '../../app/api/teams';

const mockMemberService = vi.mocked(MemberService);
const mockToonService = vi.mocked(ToonService);
const mockGuildService = vi.mocked(GuildService);
const mockTeamService = vi.mocked(TeamService);

const mockMember = {
  id: 1,
  display_name: 'Test Member',
  guild_id: 1,
  team_id: 1,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockToons = [
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

const mockGuild = {
  id: 1,
  name: 'Test Guild',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockTeam = {
  id: 1,
  name: 'Test Team',
  guild_id: 1,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockTeams = [mockTeam];

const renderMember = (loaderData: any) => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <MemberDetail loaderData={loaderData} />
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Member Detail Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementations
    mockMemberService.getMember.mockResolvedValue(mockMember);
    mockToonService.getToonsByMember.mockResolvedValue(mockToons);
    mockGuildService.getGuild.mockResolvedValue(mockGuild);
    mockTeamService.getTeams.mockResolvedValue(mockTeams);
    mockTeamService.getTeam.mockResolvedValue(mockTeam);
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Loader Function', () => {
    it('should load member data successfully', async () => {
      const result = await loader({ params: { id: '1' } });
      
      expect(result).toEqual({
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      });
      
      expect(mockMemberService.getMember).toHaveBeenCalledWith(1);
      expect(mockToonService.getToonsByMember).toHaveBeenCalledWith(1);
      expect(mockGuildService.getGuild).toHaveBeenCalledWith(1);
      expect(mockTeamService.getTeam).toHaveBeenCalledWith(1);
    });

    it('should handle member not found', async () => {
      mockMemberService.getMember.mockRejectedValue(new Error('Member not found'));
      
      await expect(loader({ params: { id: '999' } })).rejects.toThrow('Failed to load member data');
    });

    it('should handle missing team gracefully', async () => {
      const memberWithoutTeam = { ...mockMember, team_id: undefined };
      mockMemberService.getMember.mockResolvedValue(memberWithoutTeam);
      
      const result = await loader({ params: { id: '1' } });
      
      expect(result.guild).toEqual(mockGuild);
      expect(result.team).toBeNull();
      expect(mockGuildService.getGuild).toHaveBeenCalledWith(1);
      expect(mockTeamService.getTeam).not.toHaveBeenCalled();
    });
  });

  describe('Component Rendering', () => {
    it('should render member information correctly', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      renderMember(loaderData);
      
      // Check for member name in the main heading
      expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      expect(screen.getByText('Test Guild')).toBeInTheDocument();
      expect(screen.getByText('Test Team')).toBeInTheDocument();
    });

    it('should render toons correctly', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      renderMember(loaderData);
      
      expect(screen.getByText('TestToon')).toBeInTheDocument();
      expect(screen.getByText('Warrior')).toBeInTheDocument();
      expect(screen.getByText('Tank')).toBeInTheDocument();
      expect(screen.getByText('Main')).toBeInTheDocument();
    });

    it('should show empty state when no toons exist', async () => {
      const loaderData = {
        member: mockMember,
        toons: [],
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      renderMember(loaderData);
      
      expect(screen.getByText('No Characters Found')).toBeInTheDocument();
      expect(screen.getByText('Add First Character')).toBeInTheDocument();
    });

    it('should show member not found when member is null', async () => {
      const loaderData = {
        member: null,
        toons: [],
        teams: [],
        guild: null,
        team: null,
      };
      
      renderMember(loaderData);
      
      expect(screen.getByText('Member Not Found')).toBeInTheDocument();
      expect(screen.getByText('Back to Members')).toBeInTheDocument();
    });
  });

  describe('Toon Management', () => {
    it('should show toon form when add character button is clicked', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      renderMember(loaderData);
      
      const addButton = screen.getByText('Add Character');
      fireEvent.click(addButton);
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Add Toon' })).toBeInTheDocument(); // Form title
        expect(screen.getByLabelText('Username')).toBeInTheDocument();
      });
    });

    it('should handle toon creation', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      const { id, ...toonWithoutId } = mockToons[0];
      mockToonService.createToon.mockResolvedValue({ id: 2, ...toonWithoutId });
      mockToonService.getToonsByMember.mockResolvedValue([...mockToons, { id: 2, ...toonWithoutId }]);
      
      renderMember(loaderData);
      
      const addButton = screen.getByText('Add Character');
      fireEvent.click(addButton);
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Add Toon' })).toBeInTheDocument();
      });
      
      // Fill out form and submit
      const nameInput = screen.getByLabelText('Username');
      fireEvent.change(nameInput, { target: { value: 'NewToon' } });
      
      const classSelect = screen.getByLabelText('Class');
      fireEvent.change(classSelect, { target: { value: 'Warrior' } });
      
      const roleSelect = screen.getByLabelText('Role');
      fireEvent.change(roleSelect, { target: { value: 'Tank' } });
      
      const submitButton = screen.getByTestId('toon-form-submit');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockToonService.createToon).toHaveBeenCalled();
      });
    });

    it('should handle toon deletion', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      // Mock confirm to return true
      global.confirm = vi.fn(() => true);
      
      renderMember(loaderData);
      
      const deleteButton = screen.getByText('Delete');
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        expect(mockToonService.deleteToon).toHaveBeenCalledWith(1);
      });
    });
  });

  describe('Navigation', () => {
    it('should have correct breadcrumb navigation', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      renderMember(loaderData);
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Members')).toBeInTheDocument();
      // Check for member name in breadcrumb specifically
      const breadcrumbMember = screen.getByText('Test Member', { selector: 'span.text-slate-300' });
      expect(breadcrumbMember).toBeInTheDocument();
    });

    it('should have back to members button', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      renderMember(loaderData);
      
      expect(screen.getByText('Back to Members')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const loaderData = {
        member: mockMember,
        toons: mockToons,
        teams: mockTeams,
        guild: mockGuild,
        team: mockTeam,
      };
      
      mockToonService.createToon.mockRejectedValue(new Error('API Error'));
      
      renderMember(loaderData);
      
      const addButton = screen.getByText('Add Character');
      fireEvent.click(addButton);
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Add Toon' })).toBeInTheDocument();
      });
      
      // Fill out required form fields
      const nameInput = screen.getByLabelText('Username');
      fireEvent.change(nameInput, { target: { value: 'TestToon' } });
      
      const classSelect = screen.getByLabelText('Class');
      fireEvent.change(classSelect, { target: { value: 'Warrior' } });
      
      const roleSelect = screen.getByLabelText('Role');
      fireEvent.change(roleSelect, { target: { value: 'Tank' } });
      
      // Try to submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to create toon')).toBeInTheDocument();
      });
    });
  });
}); 