import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RaidForm } from '../../app/components/ui/RaidForm';

// Mock the API services
vi.mock('../../app/api/raids', () => ({
  RaidService: {
    processWarcraftLogs: vi.fn(),
  },
}));

vi.mock('../../app/api/toons', () => ({
  ToonService: {
    createToon: vi.fn(),
  },
}));

import { RaidService } from '../../app/api/raids';
import { ToonService } from '../../app/api/toons';

const mockTeams = [
  { id: 1, name: 'Team Alpha', guild_id: 1, created_at: '', updated_at: '' },
  { id: 2, name: 'Team Beta', guild_id: 1, created_at: '', updated_at: '' },
];
const mockScenarios = [
  { id: 10, name: 'Black Temple', difficulty: 'Heroic', size: '25', is_active: true, created_at: '', updated_at: '' },
  { id: 11, name: 'Serpentshrine', difficulty: 'Normal', size: '25', is_active: true, created_at: '', updated_at: '' },
];

const mockWarcraftLogsResult = {
  success: true,
  report_metadata: {
    title: 'Mythic Amirdrassil, the Dream\'s Hope',
    startTime: 1703123456789,
    endTime: 1703126789012,
    owner: { name: 'TestGuild' },
    zone: { name: 'Amirdrassil, the Dream\'s Hope' },
  },
  participants: [
    { id: '1', canonicalID: '1', name: 'PlayerOne', class: 'Mage', classID: 8 },
    { id: '2', canonicalID: '2', name: 'PlayerTwo', class: 'Warrior', classID: 1 },
  ],
  matched_participants: [
    {
      toon: { id: 1, username: 'PlayerOne', class: 'Mage', role: 'DPS', is_main: true, member_id: 1, member_name: 'Member One' },
      participant: { id: '1', canonicalID: '1', name: 'PlayerOne', class: 'Mage', classID: 8 },
      is_present: true,
      notes: 'Present in WarcraftLogs report as PlayerOne',
    },
  ],
  unknown_participants: [
    {
      participant: { id: '2', canonicalID: '2', name: 'PlayerTwo', class: 'Warrior', classID: 1 },
      suggested_member: null,
      notes: 'Unknown participant: PlayerTwo',
    },
  ],
  attendance_records: [
    { toon_id: 1, is_present: true, notes: 'Present in WarcraftLogs report as PlayerOne' },
  ],
  team_toons: [
    { id: 1, username: 'PlayerOne', class: 'Mage', role: 'DPS', is_main: true, member_id: 1, member_name: 'Member One' },
  ],
};

describe('RaidForm', () => {
  let onSubmit: any;
  let onCancel: any;

  beforeEach(() => {
    onSubmit = vi.fn();
    onCancel = vi.fn();
    vi.clearAllMocks();
  });

  it('renders all fields and enables submit when teams and scenarios are available', () => {
    render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
    expect(screen.getByLabelText(/WarcraftLogs URL/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Team/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Scenario/i)).toBeInTheDocument();
    // Submit button should be enabled when team and scenario are auto-selected
    expect(screen.getByRole('button', { name: /Add Raid/i })).not.toBeDisabled();
  });

  it('enables submit when all required fields are filled and calls onSubmit', async () => {
    render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
    fireEvent.change(screen.getByLabelText(/WarcraftLogs URL/i), { target: { value: 'https://www.warcraftlogs.com/reports/abc123' } });
    fireEvent.change(screen.getByLabelText(/Team/i), { target: { value: '2' } });
    fireEvent.change(screen.getByLabelText(/Scenario/i), { target: { value: '11' } });
    expect(screen.getByRole('button', { name: /Add Raid/i })).not.toBeDisabled();
    
    // Mock the WarcraftLogs processing to return a result
    vi.mocked(RaidService.processWarcraftLogs).mockResolvedValue(mockWarcraftLogsResult);
    
    fireEvent.click(screen.getByRole('button', { name: /Add Raid/i }));
    
    // Wait for processing to complete and results to show
    await waitFor(() => {
      expect(screen.getByText(/Create Raid with Attendance/i)).toBeInTheDocument();
    });
    
    // Click the proceed button to actually submit
    fireEvent.click(screen.getByRole('button', { name: /Create Raid with Attendance/i }));
    
    expect(onSubmit).toHaveBeenCalledWith({
      warcraftlogs_url: 'https://www.warcraftlogs.com/reports/abc123',
      team_id: 2,
      scenario_id: 11,
    });
  });

  it('disables submit when no teams or scenarios are available', () => {
    render(<RaidForm teams={[]} scenarios={[]} onSubmit={onSubmit} onCancel={onCancel} />);
    // The submit button should be disabled when no teams or scenarios are available
    expect(screen.getByRole('button', { name: /Add Raid/i })).toBeDisabled();
  });

  it('disables form and shows message if no teams or scenarios', () => {
    render(<RaidForm teams={[]} scenarios={[]} onSubmit={onSubmit} onCancel={onCancel} />);
    expect(screen.getByText(/You must have at least one team and one scenario/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Add Raid/i })).toBeDisabled();
    expect(screen.getByLabelText(/WarcraftLogs URL/i)).toBeDisabled();
    expect(screen.getByLabelText(/Team/i)).toBeDisabled();
    expect(screen.getByLabelText(/Scenario/i)).toBeDisabled();
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
    fireEvent.click(screen.getByRole('button', { name: /Cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });

  it('submits immediately when no WarcraftLogs URL is provided', () => {
    render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
    
    // Change team and scenario but leave WarcraftLogs URL empty
    fireEvent.change(screen.getByLabelText(/Team/i), { target: { value: '2' } });
    fireEvent.change(screen.getByLabelText(/Scenario/i), { target: { value: '11' } });
    
    fireEvent.click(screen.getByRole('button', { name: /Add Raid/i }));
    
    expect(onSubmit).toHaveBeenCalledWith({
      warcraftlogs_url: '',
      team_id: 2,
      scenario_id: 11,
    });
  });

  describe('WarcraftLogs Processing', () => {
    it('shows processing indicator when WarcraftLogs URL is submitted', async () => {
      vi.mocked(RaidService.processWarcraftLogs).mockResolvedValue(mockWarcraftLogsResult);
      
      render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
      
      fireEvent.change(screen.getByLabelText(/WarcraftLogs URL/i), { 
        target: { value: 'https://www.warcraftlogs.com/reports/abc123' } 
      });
      fireEvent.click(screen.getByRole('button', { name: /Add Raid/i }));

      await waitFor(() => {
        expect(screen.getByText(/Processing WarcraftLogs Report/i)).toBeInTheDocument();
      });
    });

    it('shows WarcraftLogs results after successful processing', async () => {
      vi.mocked(RaidService.processWarcraftLogs).mockResolvedValue(mockWarcraftLogsResult);
      
      render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
      
      fireEvent.change(screen.getByLabelText(/WarcraftLogs URL/i), { 
        target: { value: 'https://www.warcraftlogs.com/reports/abc123' } 
      });
      fireEvent.click(screen.getByRole('button', { name: /Add Raid/i }));

      await waitFor(() => {
        expect(screen.getByText(/WarcraftLogs Report Analysis/i)).toBeInTheDocument();
        expect(screen.getByText(/Mythic Amirdrassil, the Dream's Hope/i)).toBeInTheDocument();
        // Use getAllByText to handle multiple elements with the same text
        expect(screen.getAllByText(/PlayerOne/i)).toHaveLength(2); // One in name, one in notes
        expect(screen.getByText(/Member One/i)).toBeInTheDocument();
        expect(screen.getByText(/PlayerTwo/i)).toBeInTheDocument();
      });
    });

    it('shows error when WarcraftLogs processing fails', async () => {
      vi.mocked(RaidService.processWarcraftLogs).mockRejectedValue(new Error('API Error'));
      
      render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
      
      fireEvent.change(screen.getByLabelText(/WarcraftLogs URL/i), { 
        target: { value: 'https://www.warcraftlogs.com/reports/abc123' } 
      });
      fireEvent.click(screen.getByRole('button', { name: /Add Raid/i }));

      await waitFor(() => {
        expect(screen.getByText(/API Error/i)).toBeInTheDocument();
      });
    });

    it('proceeds with raid creation after successful processing', async () => {
      vi.mocked(RaidService.processWarcraftLogs).mockResolvedValue(mockWarcraftLogsResult);
      
      render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
      
      fireEvent.change(screen.getByLabelText(/WarcraftLogs URL/i), { 
        target: { value: 'https://www.warcraftlogs.com/reports/abc123' } 
      });
      fireEvent.click(screen.getByRole('button', { name: /Add Raid/i }));

      await waitFor(() => {
        expect(screen.getByText(/Create Raid with Attendance/i)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /Create Raid with Attendance/i }));

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          warcraftlogs_url: 'https://www.warcraftlogs.com/reports/abc123',
          team_id: 1,
          scenario_id: 10,
        });
      });
    });

    it('shows WarcraftLogs processing hint when URL is entered', () => {
      render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
      
      fireEvent.change(screen.getByLabelText(/WarcraftLogs URL/i), { 
        target: { value: 'https://www.warcraftlogs.com/reports/abc123' } 
      });

      expect(screen.getByText(/This will automatically process attendance/i)).toBeInTheDocument();
    });
  });
}); 