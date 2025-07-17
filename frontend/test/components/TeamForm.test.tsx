import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { TeamForm } from '../../app/components/ui/TeamForm';
import type { Team, Guild } from '../../app/api/types';

// Mock data
const mockGuilds: Guild[] = [
  { id: 1, name: 'Test Guild 1', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, name: 'Test Guild 2', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockTeam: Team = {
  id: 1,
  name: 'Test Team',
  guild_id: 1,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const defaultProps = {
  mode: 'add' as const,
  guilds: mockGuilds,
  onSubmit: vi.fn(),
  onCancel: vi.fn(),
};

const renderTeamForm = (props = {}) => {
  return render(
    <MemoryRouter>
      <TeamForm {...defaultProps} {...props} />
    </MemoryRouter>
  );
};

describe('TeamForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Add Mode', () => {
    it('renders add form with correct title', () => {
      renderTeamForm();
      // Use getByRole for heading
      expect(screen.getByRole('heading', { name: /Add Team/i })).toBeInTheDocument();
    });

    it('renders empty form fields', () => {
      renderTeamForm();
      expect(screen.getByLabelText('Team Name')).toHaveValue('');
      expect(screen.getByLabelText('Guild')).toHaveValue('');
    });

    it('renders guild options', () => {
      renderTeamForm();
      const guildSelect = screen.getByLabelText('Guild');
      expect(guildSelect).toHaveDisplayValue('Select a guild');
      expect(screen.getByText('Test Guild 1')).toBeInTheDocument();
      expect(screen.getByText('Test Guild 2')).toBeInTheDocument();
    });

    it('shows validation errors when submitting empty form', async () => {
      renderTeamForm();
      
      const submitButton = screen.getByTestId('team-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Guild is required')).toBeInTheDocument();
      });
    });

    it('submits form with valid data', async () => {
      const onSubmit = vi.fn();
      renderTeamForm({ onSubmit });

      // Fill form
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'New Team' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('team-form-submit');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          name: 'New Team',
          guild_id: 1,
        });
      });
    });

    it('trims whitespace from team name', async () => {
      const onSubmit = vi.fn();
      renderTeamForm({ onSubmit });

      // Fill form with whitespace
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: '  New Team  ' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('team-form-submit');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          name: 'New Team',
          guild_id: 1,
        });
      });
    });

    it('calls onCancel when cancel button is clicked', () => {
      const onCancel = vi.fn();
      renderTeamForm({ onCancel });

      fireEvent.click(screen.getByText('Cancel'));
      expect(onCancel).toHaveBeenCalled();
    });

    it('disables submit button when form is invalid', () => {
      renderTeamForm();
      
      const submitButton = screen.getByTestId('team-form-submit');
      expect(submitButton).toBeDisabled();
    });

    it('enables submit button when form is valid', async () => {
      renderTeamForm();

      // Fill form
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'New Team' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '1' },
      });

      // Wait for button to be enabled
      await waitFor(() => {
        const submitButton = screen.getByTestId('team-form-submit');
        expect(submitButton).not.toBeDisabled();
      });
    });
  });

  describe('Edit Mode', () => {
    it('renders edit form with correct title', () => {
      renderTeamForm({ mode: 'edit' });
      expect(screen.getByText('Edit Team')).toBeInTheDocument();
    });

    it('populates form with initial values', () => {
      renderTeamForm({
        mode: 'edit',
        initialValues: mockTeam,
      });

      expect(screen.getByLabelText('Team Name')).toHaveValue('Test Team');
      expect(screen.getByLabelText('Guild')).toHaveValue('1');
    });

    it('submits form with updated data', async () => {
      const onSubmit = vi.fn();
      renderTeamForm({
        mode: 'edit',
        initialValues: mockTeam,
        onSubmit,
      });

      // Update form
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'Updated Team' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '2' },
      });

      // Submit form
      const submitButton = screen.getByTestId('team-form-submit');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          name: 'Updated Team',
          guild_id: 2,
        });
      });
    });
  });

  describe('Loading State', () => {
    it('shows loading text on submit button when loading', () => {
      renderTeamForm({ loading: true });
      
      expect(screen.getByText('Adding...')).toBeInTheDocument();
    });

    it('shows saving text on submit button when editing and loading', () => {
      renderTeamForm({ mode: 'edit', loading: true });
      
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });

    it('disables form fields when loading', () => {
      renderTeamForm({ loading: true });
      
      expect(screen.getByLabelText('Team Name')).toBeDisabled();
      expect(screen.getByLabelText('Guild')).toBeDisabled();
      expect(screen.getByText('Cancel')).toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    it('displays error message when provided', () => {
      const errorMessage = 'Failed to create team';
      renderTeamForm({ error: errorMessage });
      
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    it('does not display error message when not provided', () => {
      renderTeamForm();
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('shows name error when name is empty', async () => {
      renderTeamForm();

      // Fill only guild
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('team-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.queryByText('Guild is required')).not.toBeInTheDocument();
      });
    });

    it('shows guild error when guild is not selected', async () => {
      renderTeamForm();

      // Fill only name
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'Test Team' },
      });

      // Submit form
      const submitButton = screen.getByTestId('team-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Guild is required')).toBeInTheDocument();
        expect(screen.queryByText('Name is required')).not.toBeInTheDocument();
      });
    });

    it('clears validation errors when form becomes valid', async () => {
      renderTeamForm();

      // Submit empty form to show errors
      const submitButton = screen.getByTestId('team-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Guild is required')).toBeInTheDocument();
      });

      // Fill form to make it valid
      fireEvent.change(screen.getByLabelText('Team Name'), {
        target: { value: 'Test Team' },
      });
      fireEvent.change(screen.getByLabelText('Guild'), {
        target: { value: '1' },
      });

      // Errors should be cleared when form becomes valid
      expect(screen.queryByText('Name is required')).not.toBeInTheDocument();
      expect(screen.queryByText('Guild is required')).not.toBeInTheDocument();
    });
  });
}); 