import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import Teams from '../../app/routes/teams';
import { AuthProvider } from '../../app/contexts/AuthContext';
import { TeamService } from '../../app/api/teams';
import { GuildService } from '../../app/api/guilds';
import type { Team, Guild } from '../../app/api/types';

// Mock the API services
vi.mock('../../app/api/teams');
vi.mock('../../app/api/guilds');

const mockTeamService = vi.mocked(TeamService);
const mockGuildService = vi.mocked(GuildService);

// Mock data
const mockGuilds: Guild[] = [
  { id: 1, name: 'Test Guild 1', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, name: 'Test Guild 2', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockTeams: Team[] = [
  { id: 1, name: 'Team Alpha', guild_id: 1, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, name: 'Team Beta', guild_id: 1, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 3, name: 'Team Gamma', guild_id: 2, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const renderTeams = () => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Teams />
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Teams', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementations
    mockTeamService.getTeams.mockResolvedValue(mockTeams);
    mockGuildService.getGuilds.mockResolvedValue(mockGuilds);
  });

  describe('Loading State', () => {
    it('shows loading spinner initially', () => {
      renderTeams();
      expect(screen.getByText('Loading teams...')).toBeInTheDocument();
    });

    it('hides loading spinner after data loads', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.queryByText('Loading teams...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('shows error message when API call fails', async () => {
      mockTeamService.getTeams.mockRejectedValue(new Error('Failed to load teams'));
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Error Loading Teams')).toBeInTheDocument();
        expect(screen.getByText('Failed to load teams')).toBeInTheDocument();
      });
    });

    it('shows try again button when error occurs', async () => {
      mockTeamService.getTeams.mockRejectedValue(new Error('Failed to load teams'));
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });
    });
  });

  describe('Team List Display', () => {
    it('displays all teams after loading', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
        expect(screen.getByText('Team Gamma')).toBeInTheDocument();
      });
    });

    it('shows team count in header', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('3 of 3 teams')).toBeInTheDocument();
      });
    });

    it('displays guild information for each team', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Test Guild 1 • Team ID: 1')).toBeInTheDocument();
        expect(screen.getByText('Test Guild 2 • Team ID: 3')).toBeInTheDocument();
      });
    });

    it('shows empty state when no teams exist', async () => {
      mockTeamService.getTeams.mockResolvedValue([]);
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('No Teams Found')).toBeInTheDocument();
        expect(screen.getByText('Get started by creating your first team')).toBeInTheDocument();
        expect(screen.getByText('Create First Team')).toBeInTheDocument();
      });
    });
  });

  describe('Statistics Cards', () => {
    it('displays total teams count', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument();
        expect(screen.getByText('Total Teams')).toBeInTheDocument();
      });
    });

    it('displays teams by guild statistics', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('2')).toBeInTheDocument();
        expect(screen.getByText('Test Guild 1 Teams')).toBeInTheDocument();
      });
    });
  });

  describe('Search and Filtering', () => {
    it('filters teams by search term', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search by team name...');
      fireEvent.change(searchInput, { target: { value: 'Alpha' } });

      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.queryByText('Team Beta')).not.toBeInTheDocument();
        expect(screen.queryByText('Team Gamma')).not.toBeInTheDocument();
        expect(screen.getByText('1 of 3 teams')).toBeInTheDocument();
      });
    });

    it('filters teams by guild', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
        expect(screen.getByText('Team Gamma')).toBeInTheDocument();
      });

      const guildFilter = screen.getByLabelText('Filter by Guild');
      fireEvent.change(guildFilter, { target: { value: '2' } });

      await waitFor(() => {
        expect(screen.queryByText('Team Alpha')).not.toBeInTheDocument();
        expect(screen.queryByText('Team Beta')).not.toBeInTheDocument();
        expect(screen.getByText('Team Gamma')).toBeInTheDocument();
        expect(screen.getByText('1 of 3 teams')).toBeInTheDocument();
      });
    });

    it('combines search and guild filters', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
        expect(screen.getByText('Team Gamma')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search by team name...');
      const guildFilter = screen.getByLabelText('Filter by Guild');
      
      fireEvent.change(searchInput, { target: { value: 'Team' } });
      fireEvent.change(guildFilter, { target: { value: '1' } });

      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
        expect(screen.queryByText('Team Gamma')).not.toBeInTheDocument();
        expect(screen.getByText('2 of 3 teams')).toBeInTheDocument();
      });
    });

    it('clears filters when clear button is clicked', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
        expect(screen.getByText('Team Gamma')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search by team name...');
      const guildFilter = screen.getByLabelText('Filter by Guild');
      
      fireEvent.change(searchInput, { target: { value: 'Alpha' } });
      fireEvent.change(guildFilter, { target: { value: '1' } });

      await waitFor(() => {
        expect(screen.getByText('1 of 3 teams')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Clear Filters'));

      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
        expect(screen.getByText('Team Gamma')).toBeInTheDocument();
        expect(screen.getByText('3 of 3 teams')).toBeInTheDocument();
      });
    });

    it('shows no results message when filters return no matches', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search by team name...');
      fireEvent.change(searchInput, { target: { value: 'Nonexistent' } });

      await waitFor(() => {
        expect(screen.getByText('No Teams Match Filters')).toBeInTheDocument();
        expect(screen.getByText('Try adjusting your search or filter criteria')).toBeInTheDocument();
      });
    });
  });

  describe('Add Team', () => {
    it('opens add form when Add Team button is clicked', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Add Team')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Add Team'));

      await waitFor(() => {
        expect(screen.getByTestId('team-form-modal')).toBeInTheDocument();
        expect(screen.getByText('Add Team')).toBeInTheDocument();
      });
    });

    it('creates new team successfully', async () => {
      const newTeam: Team = {
        id: 4,
        name: 'New Team',
        guild_id: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };
      
      mockTeamService.createTeam.mockResolvedValue(newTeam);
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Add Team')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Add Team'));

      await waitFor(() => {
        expect(screen.getByTestId('team-form-modal')).toBeInTheDocument();
      });

      // Fill form
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'New Team' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '1' },
      });

      // Submit form
      fireEvent.click(screen.getByTestId('team-form-submit'));

      await waitFor(() => {
        expect(mockTeamService.createTeam).toHaveBeenCalledWith({
          name: 'New Team',
          guild_id: 1,
        });
      });

      // Modal should close and new team should appear
      await waitFor(() => {
        expect(screen.queryByTestId('team-form-modal')).not.toBeInTheDocument();
        expect(screen.getByText('New Team')).toBeInTheDocument();
      });
    });

    it('handles team creation error', async () => {
      mockTeamService.createTeam.mockRejectedValue(new Error('Failed to create team'));
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Add Team')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Add Team'));

      await waitFor(() => {
        expect(screen.getByTestId('team-form-modal')).toBeInTheDocument();
      });

      // Fill form
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'New Team' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '1' },
      });

      // Submit form
      fireEvent.click(screen.getByTestId('team-form-submit'));

      await waitFor(() => {
        expect(screen.getByText('Failed to create team')).toBeInTheDocument();
      });
    });
  });

  describe('Edit Team', () => {
    it('opens edit form when Edit button is clicked', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByText('Edit');
      fireEvent.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByTestId('team-form-modal')).toBeInTheDocument();
        expect(screen.getByText('Edit Team')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Team Alpha')).toBeInTheDocument();
      });
    });

    it('updates team successfully', async () => {
      const updatedTeam: Team = {
        id: 1,
        name: 'Updated Team Alpha',
        guild_id: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };
      
      mockTeamService.updateTeam.mockResolvedValue(updatedTeam);
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByText('Edit');
      fireEvent.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByTestId('team-form-modal')).toBeInTheDocument();
      });

      // Update form
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'Updated Team Alpha' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '2' },
      });

      // Submit form
      fireEvent.click(screen.getByTestId('team-form-submit'));

      await waitFor(() => {
        expect(mockTeamService.updateTeam).toHaveBeenCalledWith(1, {
          name: 'Updated Team Alpha',
          guild_id: 2,
        });
      });

      // Modal should close and team should be updated
      await waitFor(() => {
        expect(screen.queryByTestId('team-form-modal')).not.toBeInTheDocument();
        expect(screen.getByText('Updated Team Alpha')).toBeInTheDocument();
      });
    });
  });

  describe('Delete Team', () => {
    it('shows confirmation dialog when Delete button is clicked', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this team? This action cannot be undone.');
      
      confirmSpy.mockRestore();
    });

    it('deletes team when confirmed', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
      mockTeamService.deleteTeam.mockResolvedValue(undefined);
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(mockTeamService.deleteTeam).toHaveBeenCalledWith(1);
      });

      // Team should be removed from the list
      await waitFor(() => {
        expect(screen.queryByText('Team Alpha')).not.toBeInTheDocument();
        expect(screen.getByText('Team Beta')).toBeInTheDocument();
      });
      
      confirmSpy.mockRestore();
    });

    it('does not delete team when cancelled', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      expect(mockTeamService.deleteTeam).not.toHaveBeenCalled();
      
      confirmSpy.mockRestore();
    });

    it('handles delete error', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      mockTeamService.deleteTeam.mockRejectedValue(new Error('Failed to delete team'));
      
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Team Alpha')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Failed to delete team: Failed to delete team');
      });
      
      confirmSpy.mockRestore();
      alertSpy.mockRestore();
    });
  });

  describe('Navigation', () => {
    it('has breadcrumb navigation', async () => {
      renderTeams();
      
      await waitFor(() => {
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Teams')).toBeInTheDocument();
      });
    });

    it('has dashboard link in header', async () => {
      renderTeams();
      
      await waitFor(() => {
        const dashboardLinks = screen.getAllByText('Dashboard');
        expect(dashboardLinks.length).toBeGreaterThan(0);
      });
    });
  });
}); 