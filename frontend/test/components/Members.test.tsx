import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { createMemoryRouter, RouterProvider } from 'react-router';
import Members from '../../app/routes/members';

// Mock React Router
vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router');
  return {
    ...actual,
    Link: ({ to, children, ...props }: any) => (
      <a href={to} {...props}>
        {children}
      </a>
    ),
  };
});

// Mock API services
vi.mock('../../app/api/members', () => ({
  MemberService: {
    getMembers: vi.fn(),
  },
}));

vi.mock('../../app/api/guilds', () => ({
  GuildService: {
    getGuilds: vi.fn(),
  },
}));

vi.mock('../../app/api/teams', () => ({
  TeamService: {
    getTeams: vi.fn(),
  },
}));

vi.mock('../../app/api/toons', () => ({
  ToonService: {
    getToons: vi.fn(),
  },
}));

// Mock AuthContext
vi.mock('../../app/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      user_id: 1,
      username: 'testuser',
      is_superuser: false,
    },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    error: null,
    clearError: vi.fn(),
  }),
}));

const renderMembers = () => {
  const router = createMemoryRouter([
    {
      path: '/members',
      element: <Members />,
    },
  ], {
    initialEntries: ['/members'],
    initialIndex: 0,
  });

  return render(<RouterProvider router={router} />);
};

describe('Members', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders members page with loading state initially', () => {
    renderMembers();
    expect(screen.getByText('Loading members...')).toBeInTheDocument();
  });

  it('renders members page with data when loaded', async () => {
    const { MemberService } = await import('../../app/api/members');
    const { GuildService } = await import('../../app/api/guilds');
    const { TeamService } = await import('../../app/api/teams');
    const { ToonService } = await import('../../app/api/toons');
    
    // Mock successful API responses
    vi.mocked(MemberService.getMembers).mockResolvedValue([
      { id: 1, name: 'Test Member', guild_id: 1, team_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Test Guild', realm: 'Test Realm', faction: 'Alliance', created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(TeamService.getTeams).mockResolvedValue([
      { id: 1, name: 'Test Team', guild_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(ToonService.getToons).mockResolvedValue([
      { id: 1, name: 'TestToon', class_name: 'Warrior', role: 'Tank', is_main: true, member_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);

    renderMembers();

    await waitFor(() => {
      expect(screen.getByText('Guild Members')).toBeInTheDocument();
      expect(screen.getByText('Manage your guild\'s member roster and team assignments')).toBeInTheDocument();
    });

    // Check statistics cards
    expect(screen.getByText('Total Members')).toBeInTheDocument();
    expect(screen.getByText('Assigned to Teams')).toBeInTheDocument();
    expect(screen.getByText('Unassigned')).toBeInTheDocument();
    expect(screen.getByText('Total Characters')).toBeInTheDocument();
  });

  it('renders error state when API calls fail', async () => {
    const { MemberService } = await import('../../app/api/members');
    vi.mocked(MemberService.getMembers).mockRejectedValue(new Error('API Error'));

    renderMembers();

    await waitFor(() => {
      expect(screen.getByText('Error Loading Members')).toBeInTheDocument();
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('shows empty state when no members found', async () => {
    const { MemberService } = await import('../../app/api/members');
    const { GuildService } = await import('../../app/api/guilds');
    const { TeamService } = await import('../../app/api/teams');
    const { ToonService } = await import('../../app/api/toons');
    
    vi.mocked(MemberService.getMembers).mockResolvedValue([]);
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    vi.mocked(TeamService.getTeams).mockResolvedValue([]);
    vi.mocked(ToonService.getToons).mockResolvedValue([]);

    renderMembers();

    await waitFor(() => {
      expect(screen.getByText('No Members Found')).toBeInTheDocument();
      expect(screen.getByText('Get started by adding your first guild member')).toBeInTheDocument();
    });
  });

  it('displays search and filter controls', async () => {
    const { MemberService } = await import('../../app/api/members');
    const { GuildService } = await import('../../app/api/guilds');
    const { TeamService } = await import('../../app/api/teams');
    const { ToonService } = await import('../../app/api/toons');
    
    vi.mocked(MemberService.getMembers).mockResolvedValue([]);
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    vi.mocked(TeamService.getTeams).mockResolvedValue([]);
    vi.mocked(ToonService.getToons).mockResolvedValue([]);

    renderMembers();

    await waitFor(() => {
      expect(screen.getByText('Search Members')).toBeInTheDocument();
      expect(screen.getByText('Filter by Guild')).toBeInTheDocument();
      expect(screen.getByText('Filter by Team')).toBeInTheDocument();
      expect(screen.getByText('Clear Filters')).toBeInTheDocument();
    });
  });

  it('shows member table with correct columns', async () => {
    const { MemberService } = await import('../../app/api/members');
    const { GuildService } = await import('../../app/api/guilds');
    const { TeamService } = await import('../../app/api/teams');
    const { ToonService } = await import('../../app/api/toons');
    
    vi.mocked(MemberService.getMembers).mockResolvedValue([
      { id: 1, name: 'Test Member', guild_id: 1, team_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Test Guild', realm: 'Test Realm', faction: 'Alliance', created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(TeamService.getTeams).mockResolvedValue([
      { id: 1, name: 'Test Team', guild_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(ToonService.getToons).mockResolvedValue([]);

    renderMembers();

    await waitFor(() => {
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Guild')).toBeInTheDocument();
      expect(screen.getByText('Team')).toBeInTheDocument();
      expect(screen.getByText('Characters')).toBeInTheDocument();
      expect(screen.getByText('Actions')).toBeInTheDocument();
    });
  });
}); 