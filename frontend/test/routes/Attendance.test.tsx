import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import Attendance from '../../app/routes/attendance';
import { AuthProvider } from '../../app/contexts/AuthContext';

// Mock the API services
vi.mock('../../app/api/attendance');
vi.mock('../../app/api/raids');
vi.mock('../../app/api/toons');
vi.mock('../../app/api/teams');
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
import { AttendanceService } from '../../app/api/attendance';
import { RaidService } from '../../app/api/raids';
import { ToonService } from '../../app/api/toons';
import { TeamService } from '../../app/api/teams';

const mockAttendanceService = vi.mocked(AttendanceService);
const mockRaidService = vi.mocked(RaidService);
const mockToonService = vi.mocked(ToonService);
const mockTeamService = vi.mocked(TeamService);

const mockAttendance = [
  {
    id: 1,
    raid_id: 1,
    toon_id: 1,
    is_present: true,
    notes: 'On time',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    raid_id: 1,
    toon_id: 2,
    is_present: false,
    notes: 'No show',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const mockRaids = [
  {
    id: 1,
    scheduled_at: '2024-01-20T20:00:00Z',
    team_id: 1,
    scenario_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const mockToons = [
  {
    id: 1,
    username: 'PlayerName1',
    class: 'Mage',
    role: 'DPS',
    is_main: true,
    member_id: 1,
    team_ids: [1],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    username: 'PlayerName2',
    class: 'Tank',
    role: 'Tank',
    is_main: true,
    member_id: 2,
    team_ids: [1],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const mockTeams = [
  { id: 1, name: 'Team Alpha', guild_id: 1, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const renderAttendance = () => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Attendance />
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Attendance', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementations
    mockAttendanceService.getAttendance.mockResolvedValue(mockAttendance);
    mockRaidService.getRaids.mockResolvedValue(mockRaids);
    mockToonService.getToons.mockResolvedValue(mockToons);
    mockTeamService.getTeams.mockResolvedValue(mockTeams);
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('should render loading state initially', () => {
    renderAttendance();
    expect(screen.getByText('Loading attendance...')).toBeInTheDocument();
  });

  it('should render attendance list after loading', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.getByText('Record #2')).toBeInTheDocument();
    });
  });

  it('should display attendance statistics correctly', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // Total records
      expect(screen.getByText('1')).toBeInTheDocument(); // Present records
      expect(screen.getByText('50%')).toBeInTheDocument(); // Attendance rate
    });
  });

  it('should display toon and raid information correctly', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('PlayerName1 (Mage - DPS)')).toBeInTheDocument();
      expect(screen.getByText('PlayerName2 (Tank - Tank)')).toBeInTheDocument();
      expect(screen.getByText(/Raid #1/)).toBeInTheDocument();
    });
  });

  it('should handle search functionality', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.getByText('Record #2')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by ID, toon, or class...');
    fireEvent.change(searchInput, { target: { value: 'Mage' } });

    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.queryByText('Record #2')).not.toBeInTheDocument();
    });
  });

  it('should handle date filtering', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.getByText('Record #2')).toBeInTheDocument();
    });

    const dateInput = screen.getByLabelText('Date');
    fireEvent.change(dateInput, { target: { value: '2024-01-20' } });

    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.getByText('Record #2')).toBeInTheDocument();
    });
  });

  it('should handle team filtering', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
    });

    const teamSelect = screen.getByLabelText('Team');
    fireEvent.change(teamSelect, { target: { value: '1' } });

    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.getByText('Record #2')).toBeInTheDocument();
    });
  });

  it('should handle status filtering', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.getByText('Record #2')).toBeInTheDocument();
    });

    const statusSelect = screen.getByLabelText('Status');
    fireEvent.change(statusSelect, { target: { value: 'present' } });

    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.queryByText('Record #2')).not.toBeInTheDocument();
    });
  });

  it('should clear filters when clear button is clicked', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by ID, toon, or class...');
    const clearButton = screen.getByText('Clear Filters');
    
    fireEvent.change(searchInput, { target: { value: 'Mage' } });
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(searchInput).toHaveValue('');
      expect(screen.getByText('Record #1')).toBeInTheDocument();
      expect(screen.getByText('Record #2')).toBeInTheDocument();
    });
  });

  it('should show add attendance form when add button is clicked', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Add Record')).toBeInTheDocument();
    });

    const addButton = screen.getByText('Add Record');
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Add Attendance' })).toBeInTheDocument();
      expect(screen.getByLabelText('Raid')).toBeInTheDocument();
      expect(screen.getByLabelText('Toon')).toBeInTheDocument();
    });
  });

  it('should show edit attendance form when edit button is clicked', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Edit Attendance')).toBeInTheDocument();
    });
  });

  it('should handle attendance deletion', async () => {
    const mockDelete = mockAttendanceService.deleteAttendance.mockResolvedValue();
    const mockGetAttendance = mockAttendanceService.getAttendance;
    
    // Mock confirm to return true
    global.confirm = vi.fn(() => true);
    
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith(1);
      expect(mockGetAttendance).toHaveBeenCalledTimes(2); // Initial load + reload
    });
  });

  it('should not delete attendance when confirmation is cancelled', async () => {
    const mockDelete = mockAttendanceService.deleteAttendance;
    
    // Mock confirm to return false
    global.confirm = vi.fn(() => false);
    
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockDelete).not.toHaveBeenCalled();
    });
  });

  it('should handle error state', async () => {
    mockAttendanceService.getAttendance.mockRejectedValue(new Error('Failed to load attendance'));
    
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Error Loading Attendance')).toBeInTheDocument();
      expect(screen.getByText('Failed to load attendance')).toBeInTheDocument();
    });
  });

  it('should show empty state when no attendance records exist', async () => {
    mockAttendanceService.getAttendance.mockResolvedValue([]);
    
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('No attendance records yet')).toBeInTheDocument();
      expect(screen.getByText('Add First Record')).toBeInTheDocument();
    });
  });

  it('should show no results when search has no matches', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Record #1')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by ID, toon, or class...');
    fireEvent.change(searchInput, { target: { value: 'NonExistent' } });

    await waitFor(() => {
      expect(screen.getByText('No records found')).toBeInTheDocument();
    });
  });

  it('should display present and absent records with different styling', async () => {
    renderAttendance();
    
    await waitFor(() => {
      expect(screen.getByText('Present')).toBeInTheDocument();
      expect(screen.getByText('Absent')).toBeInTheDocument();
    });
  });
}); 