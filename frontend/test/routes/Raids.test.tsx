import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import Raids from '../../app/routes/raids';
import { AuthProvider } from '../../app/contexts/AuthContext';

// Mock the API services
vi.mock('../../app/api/raids');
vi.mock('../../app/api/teams');
vi.mock('../../app/api/scenarios');
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
import { RaidService } from '../../app/api/raids';
import { TeamService } from '../../app/api/teams';
import { ScenarioService } from '../../app/api/scenarios';

const mockRaidService = vi.mocked(RaidService);
const mockTeamService = vi.mocked(TeamService);
const mockScenarioService = vi.mocked(ScenarioService);

const mockRaids = [
  {
    id: 1,
    scheduled_at: '2024-01-20T20:00:00Z', // Later date - will appear first due to sorting
    team_id: 1,
    scenario_name: 'Blackrock Foundry',
    scenario_difficulty: 'Normal',
    scenario_size: '10',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    scheduled_at: '2024-01-15T20:00:00Z', // Earlier date - will appear second due to sorting
    team_id: 2,
    scenario_name: 'Hellfire Citadel',
    scenario_difficulty: 'Heroic',
    scenario_size: '25',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const mockTeams = [
  { id: 1, name: 'Team Alpha', guild_id: 1, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, name: 'Team Beta', guild_id: 1, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockScenarios = [
  { id: 1, name: 'Blackrock Foundry', difficulty: 'Normal', size: '10', is_active: true, mop: false, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, name: 'Hellfire Citadel', difficulty: 'Heroic', size: '25', is_active: true, mop: false, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const renderRaids = () => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Raids />
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Raids', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementations
    mockRaidService.getRaids.mockResolvedValue(mockRaids);
    mockTeamService.getTeams.mockResolvedValue(mockTeams);
    mockScenarioService.getScenarios.mockResolvedValue(mockScenarios);
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('should render loading state initially', () => {
    renderRaids();
    expect(screen.getByText('Loading raids...')).toBeInTheDocument();
  });

  it('should render raids list after loading', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
      expect(screen.getByText('Raid #2')).toBeInTheDocument();
    });
  });

  it('should display team and scenario names correctly', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Team Alpha')).toBeInTheDocument();
      expect(screen.getByText('Team Beta')).toBeInTheDocument();
      expect(screen.getByText('Blackrock Foundry (Normal, 10-man)')).toBeInTheDocument();
      expect(screen.getByText('Hellfire Citadel (Heroic, 25-man)')).toBeInTheDocument();
    });
  });

  it('should handle search functionality', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by ID, team, or scenario...');
    fireEvent.change(searchInput, { target: { value: 'Alpha' } });

    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
      expect(screen.queryByText('Raid #2')).not.toBeInTheDocument();
    });
  });

  it('should handle date filtering', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
      expect(screen.getByText('Raid #2')).toBeInTheDocument();
    });

    const dateInput = screen.getByLabelText('Filter by Date');
    fireEvent.change(dateInput, { target: { value: '2024-01-15' } });

    await waitFor(() => {
      expect(screen.queryByText('Raid #1')).not.toBeInTheDocument(); // Raid #1 has date 2024-01-20
      expect(screen.getByText('Raid #2')).toBeInTheDocument(); // Raid #2 has date 2024-01-15
    });
  });

  it('should clear filters when clear button is clicked', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by ID, team, or scenario...');
    const clearButton = screen.getByText('Clear Filters');
    
    fireEvent.change(searchInput, { target: { value: 'Alpha' } });
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(searchInput).toHaveValue('');
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
      expect(screen.getByText('Raid #2')).toBeInTheDocument();
    });
  });

  it('should show add raid form when add button is clicked', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Add Raid')).toBeInTheDocument();
    });

    const addButton = screen.getByText('Add Raid');
    fireEvent.click(addButton);

    await waitFor(() => {
      // Look for the form title specifically (h2 element)
      expect(screen.getByRole('heading', { name: 'Add Raid' })).toBeInTheDocument();
      expect(screen.getByLabelText('Team')).toBeInTheDocument();
      expect(screen.getByLabelText('Scenario Variation')).toBeInTheDocument();
    });
  });

  it('should show edit raid form when edit button is clicked', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Edit Raid')).toBeInTheDocument();
    });
  });

  it('should handle raid deletion', async () => {
    const mockDelete = mockRaidService.deleteRaid.mockResolvedValue();
    const mockGetRaids = mockRaidService.getRaids;
    
    // Mock confirm to return true
    global.confirm = vi.fn(() => true);
    
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith(1); // Raid #1 appears first due to sorting by date
      expect(mockGetRaids).toHaveBeenCalledTimes(2); // Initial load + reload
    });
  });

  it('should not delete raid when confirmation is cancelled', async () => {
    const mockDelete = mockRaidService.deleteRaid;
    
    // Mock confirm to return false
    global.confirm = vi.fn(() => false);
    
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockDelete).not.toHaveBeenCalled();
    });
  });

  it('should handle error state', async () => {
    mockRaidService.getRaids.mockRejectedValue(new Error('Failed to load raids'));
    
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Error Loading Raids')).toBeInTheDocument();
      expect(screen.getByText('Failed to load raids')).toBeInTheDocument();
    });
  });

  it('should show empty state when no raids exist', async () => {
    mockRaidService.getRaids.mockResolvedValue([]);
    
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('No raids yet')).toBeInTheDocument();
      expect(screen.getByText('Add First Raid')).toBeInTheDocument();
    });
  });

  it('should show no results when search has no matches', async () => {
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Raid #1')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by ID, team, or scenario...');
    fireEvent.change(searchInput, { target: { value: 'NonExistent' } });

    await waitFor(() => {
      expect(screen.getByText('No raids found')).toBeInTheDocument();
    });
  });

  it('should display past raids with different styling', async () => {
    const pastRaid = {
      ...mockRaids[0],
      scheduled_at: '2020-01-15T20:00:00Z', // Past date
    };
    
    mockRaidService.getRaids.mockResolvedValue([pastRaid]);
    
    renderRaids();
    
    await waitFor(() => {
      expect(screen.getByText('Past')).toBeInTheDocument();
    });
  });
}); 