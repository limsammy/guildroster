import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import MemberDetail from '../../app/routes/member';

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

// Mock the AuthContext with a simple authenticated user
vi.mock('../../app/contexts/AuthContext', () => ({
  useAuth: () => ({ 
    isAuthenticated: true,
    user: { user_id: 1, username: 'testuser', is_superuser: true }
  }),
}));

// Mock useParams to return the member ID
vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router');
  return {
    ...actual,
    useParams: () => ({ id: '1' }),
  };
});

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

const renderMember = () => {
  return render(
    <MemoryRouter initialEntries={['/members/1']}>
      <MemberDetail />
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

  describe('Component Loading', () => {
    it('should load member data successfully', async () => {
      renderMember();
      
      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
      expect(mockMemberService.getMember).toHaveBeenCalledWith(1);
      expect(mockToonService.getToonsByMember).toHaveBeenCalledWith(1);
      expect(mockGuildService.getGuild).toHaveBeenCalledWith(1);
      expect(mockTeamService.getTeam).toHaveBeenCalledWith(1);
    });

    it('should handle member not found', async () => {
      mockMemberService.getMember.mockRejectedValue(new Error('Member not found'));
      
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByText('Error Loading Member')).toBeInTheDocument();
      });
    });

    it('should handle missing team gracefully', async () => {
      const memberWithoutTeam = { ...mockMember, team_id: undefined };
      mockMemberService.getMember.mockResolvedValue(memberWithoutTeam);
      
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
      expect(mockGuildService.getGuild).toHaveBeenCalledWith(1);
      expect(mockTeamService.getTeam).not.toHaveBeenCalled();
    });
  });

  describe('Component Rendering', () => {
    it('should render member information correctly', async () => {
      renderMember();
      
      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
      // Check for member name in the main heading
      expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      expect(screen.getByText('Test Guild')).toBeInTheDocument();
      expect(screen.getByText('Test Team')).toBeInTheDocument();
    });

    it('should render toons correctly', async () => {
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByText('TestToon')).toBeInTheDocument();
      });
      
      expect(screen.getByText('Warrior')).toBeInTheDocument();
      expect(screen.getByText('Tank')).toBeInTheDocument();
      expect(screen.getByText('Main')).toBeInTheDocument();
    });

    it('should show empty state when no toons exist', async () => {
      mockToonService.getToonsByMember.mockResolvedValue([]);
      
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByText('No Characters Found')).toBeInTheDocument();
      });
      expect(screen.getByText('Add First Character')).toBeInTheDocument();
    });

    it('should show member not found when member is null', async () => {
      mockMemberService.getMember.mockResolvedValue(null);
      
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByText('Member Not Found')).toBeInTheDocument();
      });
      expect(screen.getByText('Back to Members')).toBeInTheDocument();
    });
  });

  describe('Toon Management', () => {
    it('should show toon form when add character button is clicked', async () => {
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
      const addButton = screen.getByText('Add Character');
      fireEvent.click(addButton);
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Add Toon' })).toBeInTheDocument(); // Form title
        expect(screen.getByLabelText('Username')).toBeInTheDocument();
      });
    });

    it('should handle toon creation', async () => {
      const { id, ...toonWithoutId } = mockToons[0];
      mockToonService.createToon.mockResolvedValue({ id: 2, ...toonWithoutId });
      mockToonService.getToonsByMember.mockResolvedValue([...mockToons, { id: 2, ...toonWithoutId }]);
      
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
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
      // Mock confirm to return true
      global.confirm = vi.fn(() => true);
      
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
      const deleteButton = screen.getByText('Delete');
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        expect(mockToonService.deleteToon).toHaveBeenCalledWith(1);
      });
    });
  });

  describe('Navigation', () => {
    it('should have correct breadcrumb navigation', async () => {
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Members')).toBeInTheDocument();
      // Check for member name in breadcrumb specifically
      const breadcrumbMember = screen.getByText('Test Member', { selector: 'span.text-slate-300' });
      expect(breadcrumbMember).toBeInTheDocument();
    });

    it('should have back to members button', async () => {
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
      expect(screen.getByText('Back to Members')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      mockToonService.createToon.mockRejectedValue(new Error('API Error'));
      
      renderMember();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Member' })).toBeInTheDocument();
      });
      
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