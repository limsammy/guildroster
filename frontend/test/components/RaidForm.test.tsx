import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RaidForm } from '../../app/components/ui/RaidForm';

const mockTeams = [
  { id: 1, name: 'Team Alpha', guild_id: 1, created_at: '', updated_at: '' },
  { id: 2, name: 'Team Beta', guild_id: 1, created_at: '', updated_at: '' },
];
const mockScenarios = [
  { id: 10, name: 'Black Temple', difficulty: 'Heroic', size: '25', is_active: true, created_at: '', updated_at: '' },
  { id: 11, name: 'Serpentshrine', difficulty: 'Normal', size: '25', is_active: true, created_at: '', updated_at: '' },
];

describe('RaidForm', () => {
  let onSubmit: any;
  let onCancel: any;

  beforeEach(() => {
    onSubmit = vi.fn();
    onCancel = vi.fn();
  });

  it('renders all fields and enables submit when teams and scenarios are available', () => {
    render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
    expect(screen.getByLabelText(/WarcraftLogs URL/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Team/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Scenario/i)).toBeInTheDocument();
    // Submit button should be enabled when team and scenario are auto-selected
    expect(screen.getByRole('button', { name: /Add Raid/i })).not.toBeDisabled();
  });

  it('enables submit when all required fields are filled and calls onSubmit', () => {
    render(<RaidForm teams={mockTeams} scenarios={mockScenarios} onSubmit={onSubmit} onCancel={onCancel} />);
    fireEvent.change(screen.getByLabelText(/WarcraftLogs URL/i), { target: { value: 'https://www.warcraftlogs.com/reports/abc123' } });
    fireEvent.change(screen.getByLabelText(/Team/i), { target: { value: '2' } });
    fireEvent.change(screen.getByLabelText(/Scenario/i), { target: { value: '11' } });
    expect(screen.getByRole('button', { name: /Add Raid/i })).not.toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: /Add Raid/i }));
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
}); 