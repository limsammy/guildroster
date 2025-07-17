import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router';
import Guilds from '../../app/routes/guilds';
import { GuildService } from '../../app/api/guilds';

// Mock the services
vi.mock('../../app/api/guilds');
vi.mock('../../app/contexts/AuthContext', () => ({
  useAuth: () => ({ user: { user_id: 1, username: 'testuser', is_superuser: true } }),
}));

// Mock window.confirm
const mockConfirm = vi.fn();
Object.defineProperty(window, 'confirm', {
  value: mockConfirm,
  writable: true,
});

describe('Guilds Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockConfirm.mockReturnValue(true); // Default to confirming
  });

  it('renders loading state', () => {
    vi.mocked(GuildService.getGuilds).mockImplementation(() => new Promise(() => {}));
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    expect(screen.getByText('Loading guilds...')).toBeInTheDocument();
  });

  it('renders error state', async () => {
    vi.mocked(GuildService.getGuilds).mockRejectedValue(new Error('Failed to load'));
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Error Loading Guilds')).toBeInTheDocument());
    expect(screen.getByText('Failed to load')).toBeInTheDocument();
  });

  it('renders empty state when no guilds', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('No Guilds Found')).toBeInTheDocument());
    expect(screen.getByText('Get started by creating your first guild')).toBeInTheDocument();
  });

  it('renders a list of guilds', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Guild One', created_at: '', updated_at: '' },
      { id: 2, name: 'Guild Two', created_at: '', updated_at: '' },
    ]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Guild One')).toBeInTheDocument();
      expect(screen.getByText('Guild Two')).toBeInTheDocument();
      expect(screen.getByText('Guild ID: 1')).toBeInTheDocument();
      expect(screen.getByText('Guild ID: 2')).toBeInTheDocument();
    });
  });

  it('opens and cancels the add guild modal', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Add Guild')).toBeInTheDocument());
    userEvent.click(screen.getByText('Add Guild'));
    await screen.findByTestId('guild-form-modal');
    userEvent.click(screen.getByRole('button', { name: /cancel/i }));
    await waitFor(() => expect(screen.queryByTestId('guild-form-modal')).not.toBeInTheDocument());
  });

  it('validates required fields in the add guild form', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Add Guild')).toBeInTheDocument());
    userEvent.click(screen.getByText('Add Guild'));
    await waitFor(() => expect(screen.getByTestId('guild-form-modal')).toBeInTheDocument());

    // Test that submit button is disabled when name is empty
    const submitButton = screen.getByTestId('guild-form-submit');
    expect(submitButton).toBeDisabled();

    // Fill in name - submit button should be enabled
    await userEvent.type(screen.getByPlaceholderText(/enter guild name/i), 'Test Guild');
    await waitFor(() => expect(submitButton).not.toBeDisabled());
  });

  it('submits the add guild form and calls createGuild', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    vi.mocked(GuildService.createGuild).mockResolvedValue({ 
      id: 1, 
      name: 'New Guild', 
      created_at: '', 
      updated_at: '' 
    });
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Add Guild')).toBeInTheDocument());
    userEvent.click(screen.getByText('Add Guild'));
    await screen.findByTestId('guild-form-modal');
    await userEvent.type(screen.getByPlaceholderText(/enter guild name/i), 'New Guild');
    const submitButton = screen.getByTestId('guild-form-submit');
    await waitFor(() => expect(submitButton).not.toBeDisabled());
    userEvent.click(submitButton);
    await waitFor(() => expect(GuildService.createGuild).toHaveBeenCalledWith({
      name: 'New Guild',
      created_by: 1,
    }));
    await waitFor(() => expect(screen.queryByTestId('guild-form-modal')).not.toBeInTheDocument());
  });

  it('opens and submits the edit guild modal', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Test Guild', created_at: '', updated_at: '' }
    ]);
    vi.mocked(GuildService.updateGuild).mockResolvedValue({ 
      id: 1, 
      name: 'Edited Guild', 
      created_at: '', 
      updated_at: '' 
    });
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Edit')).toBeInTheDocument());
    userEvent.click(screen.getByText('Edit'));
    await screen.findByTestId('guild-form-modal');
    expect(screen.getByText(/edit guild/i)).toBeInTheDocument();
    userEvent.clear(screen.getByPlaceholderText(/enter guild name/i));
    await userEvent.type(screen.getByPlaceholderText(/enter guild name/i), 'Edited Guild');
    const submitButton = screen.getByTestId('guild-form-submit');
    await waitFor(() => expect(submitButton).not.toBeDisabled());
    userEvent.click(submitButton);
    await waitFor(() => expect(GuildService.updateGuild).toHaveBeenCalled());
    await waitFor(() => expect(screen.queryByTestId('guild-form-modal')).not.toBeInTheDocument());
  });

  it('deletes a guild when confirmed', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Test Guild', created_at: '', updated_at: '' }
    ]);
    vi.mocked(GuildService.deleteGuild).mockResolvedValue();
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Delete')).toBeInTheDocument());
    userEvent.click(screen.getByText('Delete'));
    await waitFor(() => expect(mockConfirm).toHaveBeenCalledWith('Are you sure you want to delete this guild? This action cannot be undone.'));
    await waitFor(() => expect(GuildService.deleteGuild).toHaveBeenCalledWith(1));
  });

  it('filters guilds by search term', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Alliance Guild', created_at: '', updated_at: '' },
      { id: 2, name: 'Horde Guild', created_at: '', updated_at: '' },
    ]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Alliance Guild')).toBeInTheDocument());
    
    await userEvent.type(screen.getByPlaceholderText(/search by guild name/i), 'Alliance');
    expect(screen.getByText('Alliance Guild')).toBeInTheDocument();
    expect(screen.queryByText('Horde Guild')).not.toBeInTheDocument();
  });

  it('clears search when clear search button is clicked', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Alliance Guild', created_at: '', updated_at: '' },
      { id: 2, name: 'Horde Guild', created_at: '', updated_at: '' },
    ]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Alliance Guild')).toBeInTheDocument());
    
    await userEvent.type(screen.getByPlaceholderText(/search by guild name/i), 'Alliance');
    
    userEvent.click(screen.getByText('Clear Search'));
    
    // Check that search input is cleared
    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText(/search by guild name/i) as HTMLInputElement;
      expect(searchInput.value).toBe('');
    });
    
    // Check that both guilds are visible again
    expect(screen.getByText('Alliance Guild')).toBeInTheDocument();
    expect(screen.getByText('Horde Guild')).toBeInTheDocument();
  });

  it('shows error in the form if createGuild fails', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    vi.mocked(GuildService.createGuild).mockRejectedValue(new Error('Create failed'));
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Add Guild')).toBeInTheDocument());
    userEvent.click(screen.getByText('Add Guild'));
    await screen.findByTestId('guild-form-modal');
    await userEvent.type(screen.getByPlaceholderText(/enter guild name/i), 'Fail Guild');
    const submitButton = screen.getByTestId('guild-form-submit');
    await waitFor(() => expect(submitButton).not.toBeDisabled());
    userEvent.click(submitButton);
    await waitFor(() => expect(screen.getByText('Create failed')).toBeInTheDocument());
  });
}); 