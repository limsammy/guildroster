import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router';
import { GuildSwitcher } from '../app/components/ui/GuildSwitcher';
import { AuthProvider } from '../app/contexts/AuthContext';
import { GuildProvider } from '../app/contexts/GuildContext';
import { GuildService } from '../app/api/guilds';
import type { Guild } from '../app/api/types';

// Mock the API service
vi.mock('../app/api/guilds', () => ({
  GuildService: {
    getGuilds: vi.fn(),
  },
}));

// Mock AuthContext
vi.mock('../app/contexts/AuthContext', async () => {
  const actual = await vi.importActual('../app/contexts/AuthContext');
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

const mockGuilds: Guild[] = [
  { id: 1, name: 'Test Guild 1', created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
  { id: 2, name: 'Test Guild 2', created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
  { id: 3, name: 'Test Guild 3', created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
];

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <GuildProvider>
          {component}
        </GuildProvider>
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('GuildSwitcher', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    localStorageMock.setItem.mockImplementation(() => {});
    localStorageMock.removeItem.mockImplementation(() => {});
    
    // Set up default useAuth mock
    const { useAuth } = await import('../app/contexts/AuthContext');
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 1,
        username: 'testuser',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });
  });

  it('renders nothing for non-superusers', async () => {
    const { GuildService } = await import('../app/api/guilds');
    const { useAuth } = await import('../app/contexts/AuthContext');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue(mockGuilds);
    vi.mocked(useAuth).mockReturnValue({
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
    });
    
    renderWithProviders(<GuildSwitcher />);
    
    expect(screen.queryByText('Guild:')).not.toBeInTheDocument();
  });

  it('shows loading state while fetching guilds', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    // Mock a delayed response
    vi.mocked(GuildService.getGuilds).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockGuilds), 100))
    );
    
    renderWithProviders(<GuildSwitcher />);
    
    expect(screen.getByText('Loading guilds...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.queryByText('Loading guilds...')).not.toBeInTheDocument();
    });
  });

  it('shows "No guilds available" when no guilds exist', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue([]);
    
    renderWithProviders(<GuildSwitcher />);
    
    await waitFor(() => {
      expect(screen.getByText('No guilds available')).toBeInTheDocument();
    });
  });

  it('renders guild selector with available guilds', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue(mockGuilds);
    
    renderWithProviders(<GuildSwitcher />);
    
    await waitFor(() => {
      expect(screen.getByText('Guild:')).toBeInTheDocument();
    });
    
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
    
    // Check that all guilds are in the select options
    expect(screen.getByText('All Guilds')).toBeInTheDocument();
    expect(screen.getByText('Test Guild 1')).toBeInTheDocument();
    expect(screen.getByText('Test Guild 2')).toBeInTheDocument();
    expect(screen.getByText('Test Guild 3')).toBeInTheDocument();
  });

  it('allows selecting a guild', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue(mockGuilds);
    
    renderWithProviders(<GuildSwitcher />);
    
    await waitFor(() => {
      expect(screen.getByText('Guild:')).toBeInTheDocument();
    });
    
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '2' } });
    
    // Check that the clear button appears
    expect(screen.getByText('Clear')).toBeInTheDocument();
    
    // Check that localStorage was called
    expect(localStorageMock.setItem).toHaveBeenCalledWith('selectedGuildId', '2');
  });

  it('allows clearing guild selection', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue(mockGuilds);
    
    renderWithProviders(<GuildSwitcher />);
    
    await waitFor(() => {
      expect(screen.getByText('Guild:')).toBeInTheDocument();
    });
    
    // First select a guild
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '2' } });
    
    // Then clear it
    const clearButton = screen.getByText('Clear');
    fireEvent.click(clearButton);
    
    // Check that localStorage was called to remove the selection
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('selectedGuildId');
    
    // Check that the clear button is no longer visible
    expect(screen.queryByText('Clear')).not.toBeInTheDocument();
  });

  it('loads previously selected guild from localStorage', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue(mockGuilds);
    localStorageMock.getItem.mockReturnValue('2');
    
    renderWithProviders(<GuildSwitcher />);
    
    await waitFor(() => {
      expect(screen.getByText('Guild:')).toBeInTheDocument();
    });
    
    // Check that the previously selected guild is selected
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('2');
    
    // Check that the clear button is visible
    expect(screen.getByText('Clear')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    vi.mocked(GuildService.getGuilds).mockRejectedValue(new Error('API Error'));
    
    renderWithProviders(<GuildSwitcher />);
    
    await waitFor(() => {
      expect(screen.getByText('No guilds available')).toBeInTheDocument();
    });
  });

  it('selects "All Guilds" by default when no guild is selected', async () => {
    const { GuildService } = await import('../app/api/guilds');
    
    vi.mocked(GuildService.getGuilds).mockResolvedValue(mockGuilds);
    
    renderWithProviders(<GuildSwitcher />);
    
    await waitFor(() => {
      expect(screen.getByText('Guild:')).toBeInTheDocument();
    });
    
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('');
  });
}); 