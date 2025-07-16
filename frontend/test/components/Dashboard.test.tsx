import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { createMemoryRouter, RouterProvider } from 'react-router';
import Dashboard from '../../app/routes/dashboard';

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

vi.mock('../../app/api/members', () => ({
  MemberService: {
    getMembers: vi.fn(),
  },
}));

vi.mock('../../app/api/raids', () => ({
  RaidService: {
    getRaids: vi.fn(),
  },
}));

vi.mock('../../app/api/scenarios', () => ({
  ScenarioService: {
    getScenarios: vi.fn(),
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

const renderDashboard = () => {
  const router = createMemoryRouter([
    {
      path: '/dashboard',
      element: <Dashboard />,
    },
  ], {
    initialEntries: ['/dashboard'],
    initialIndex: 0,
  });

  return render(<RouterProvider router={router} />);
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard with loading state initially', () => {
    renderDashboard();
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('renders dashboard with statistics when data is loaded', async () => {
    const { GuildService } = await import('../../app/api/guilds');
    const { TeamService } = await import('../../app/api/teams');
    const { MemberService } = await import('../../app/api/members');
    const { RaidService } = await import('../../app/api/raids');
    const { ScenarioService } = await import('../../app/api/scenarios');
    
    // Mock successful API responses
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Test Guild', realm: 'Test Realm', faction: 'Alliance', created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(TeamService.getTeams).mockResolvedValue([
      { id: 1, name: 'Test Team', guild_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(MemberService.getMembers).mockResolvedValue([
      { id: 1, name: 'Test Member', guild_id: 1, team_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(RaidService.getRaids).mockResolvedValue([]);
    vi.mocked(ScenarioService.getScenarios).mockResolvedValue([
      { id: 1, name: 'Test Scenario', is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('GuildRoster Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Welcome back, testuser!')).toBeInTheDocument();
    });

    // Check statistics cards
    expect(screen.getByText('Guilds')).toBeInTheDocument();
    expect(screen.getByText('Members')).toBeInTheDocument();
    expect(screen.getByText('Total Raids')).toBeInTheDocument();
    expect(screen.getByText('Active Scenarios')).toBeInTheDocument();
    
    // Check for "Raid Teams" specifically in the statistics section (not the header)
    const raidTeamsElements = screen.getAllByText('Raid Teams');
    expect(raidTeamsElements.length).toBeGreaterThan(0);
    
    // Check that the statistics values are present (using getAllByText for multiple "1"s)
    const ones = screen.getAllByText('1');
    expect(ones).toHaveLength(4); // Should have 4 cards with value "1"
    
    const zeros = screen.getAllByText('0');
    expect(zeros).toHaveLength(1); // Should have 1 card with value "0"
  });

  it('renders error state when API calls fail', async () => {
    const { GuildService } = await import('../../app/api/guilds');
    vi.mocked(GuildService.getGuilds).mockRejectedValue(new Error('API Error'));

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Error Loading Dashboard')).toBeInTheDocument();
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('shows upcoming raids when available', async () => {
    const { GuildService } = await import('../../app/api/guilds');
    const { TeamService } = await import('../../app/api/teams');
    const { MemberService } = await import('../../app/api/members');
    const { RaidService } = await import('../../app/api/raids');
    const { ScenarioService } = await import('../../app/api/scenarios');
    
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 1);

    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    vi.mocked(TeamService.getTeams).mockResolvedValue([
      { id: 1, name: 'Test Team', guild_id: 1, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);
    vi.mocked(MemberService.getMembers).mockResolvedValue([]);
    vi.mocked(RaidService.getRaids).mockResolvedValue([
      {
        id: 1,
        scheduled_at: futureDate.toISOString(),
        difficulty: 'Normal',
        size: 10,
        team_id: 1,
        scenario_id: 1,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      }
    ]);
    vi.mocked(ScenarioService.getScenarios).mockResolvedValue([
      { id: 1, name: 'Test Scenario', is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' }
    ]);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Upcoming Raids')).toBeInTheDocument();
      expect(screen.getByText('Test Scenario')).toBeInTheDocument();
    });
  });

  it('shows empty state when no data is available', async () => {
    const { GuildService } = await import('../../app/api/guilds');
    const { TeamService } = await import('../../app/api/teams');
    const { MemberService } = await import('../../app/api/members');
    const { RaidService } = await import('../../app/api/raids');
    const { ScenarioService } = await import('../../app/api/scenarios');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    vi.mocked(TeamService.getTeams).mockResolvedValue([]);
    vi.mocked(MemberService.getMembers).mockResolvedValue([]);
    vi.mocked(RaidService.getRaids).mockResolvedValue([]);
    vi.mocked(ScenarioService.getScenarios).mockResolvedValue([]);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('No upcoming raids scheduled')).toBeInTheDocument();
      expect(screen.getByText('No raid teams found')).toBeInTheDocument();
    });
  });
}); 