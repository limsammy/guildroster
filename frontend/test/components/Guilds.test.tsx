import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router';
import Guilds from '../../app/routes/guilds';
import { GuildService } from '../../app/api/guilds';

vi.mock('../../app/api/guilds', () => ({
  GuildService: {
    getGuilds: vi.fn(),
  },
}));

// Mock AuthContext
vi.mock('../../app/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { user_id: 1, username: 'testuser', is_superuser: false },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    error: null,
    clearError: vi.fn(),
  }),
}));

describe('Guilds Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
    vi.mocked(GuildService.getGuilds).mockRejectedValue(new Error('API Error'));
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Error Loading Guilds')).toBeInTheDocument();
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('renders empty state when no guilds', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('No Guilds Found')).toBeInTheDocument();
      expect(screen.getByText('Create First Guild')).toBeInTheDocument();
    });
  });

  it('renders a list of guilds', async () => {
    vi.mocked(GuildService.getGuilds).mockResolvedValue([
      { id: 1, name: 'Guild One', realm: 'RealmA', faction: 'Alliance', created_at: '', updated_at: '' },
      { id: 2, name: 'Guild Two', realm: 'RealmB', faction: 'Horde', created_at: '', updated_at: '' },
    ]);
    render(
      <MemoryRouter>
        <Guilds />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('Guild One')).toBeInTheDocument();
      expect(screen.getByText('Guild Two')).toBeInTheDocument();
      expect(screen.getByText('RealmA • Alliance')).toBeInTheDocument();
      expect(screen.getByText('RealmB • Horde')).toBeInTheDocument();
    });
  });
}); 