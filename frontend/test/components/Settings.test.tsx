import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router';
import Settings from '../../app/routes/settings';
import { useAuth } from '../../app/contexts/AuthContext';
import { useGuild } from '../../app/contexts/GuildContext';

// Mock the UI components
vi.mock('../../app/components/ui', () => ({
  Button: ({ children, variant, className, ...props }: any) => (
    <button className={className} data-variant={variant} {...props}>
      {children}
    </button>
  ),
  Card: ({ children, variant, className, ...props }: any) => (
    <div data-testid="card" className={className} data-variant={variant} {...props}>
      {children}
    </div>
  ),
  Container: ({ children, ...props }: any) => (
    <div data-testid="container" {...props}>
      {children}
    </div>
  ),
  GuildSwitcher: () => <div data-testid="guild-switcher">Guild Switcher</div>,
}));

// Mock AuthContext
vi.mock('../../app/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
  AuthProvider: ({ children }: any) => <div>{children}</div>,
}));

// Mock GuildContext
vi.mock('../../app/contexts/GuildContext', () => ({
  useGuild: vi.fn(),
  GuildProvider: ({ children }: any) => <div>{children}</div>,
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      {component}
    </MemoryRouter>
  );
};

describe('Settings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show access denied for non-superusers', () => {
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

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByText('Access Denied')).toBeInTheDocument();
    expect(screen.getByText("You don't have permission to access settings.")).toBeInTheDocument();
    expect(screen.getByText('Return to Dashboard')).toBeInTheDocument();
  });

  it('should render settings page for superusers', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 1,
        username: 'admin',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByRole('heading', { name: 'Settings' })).toBeInTheDocument();
    expect(screen.getByText('Manage guild settings and administrative functions')).toBeInTheDocument();
  });

  it('should display guild management section', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 1,
        username: 'admin',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByText('Guild Management')).toBeInTheDocument();
    expect(screen.getByText('Manage guilds and switch between them')).toBeInTheDocument();
    expect(screen.getByText('Current Guild')).toBeInTheDocument();
    expect(screen.getByText('Guild Administration')).toBeInTheDocument();
    expect(screen.getByText('Manage Guilds')).toBeInTheDocument();
  });

  it('should display content management section', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 1,
        username: 'admin',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByText('Content Management')).toBeInTheDocument();
    expect(screen.getByText('Manage scenarios and game content')).toBeInTheDocument();
    expect(screen.getByText('Scenarios')).toBeInTheDocument();
    expect(screen.getByText('Teams')).toBeInTheDocument();
            expect(screen.getByText('Characters')).toBeInTheDocument();
  });

  it('should display system information section', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 1,
        username: 'admin',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByText('System Information')).toBeInTheDocument();
    expect(screen.getByText('Current user and system details')).toBeInTheDocument();
    expect(screen.getByText('Current User')).toBeInTheDocument();
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
  });

  it('should display user information correctly', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 123,
        username: 'testadmin',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByText('testadmin')).toBeInTheDocument();
    expect(screen.getByText('123')).toBeInTheDocument();
    expect(screen.getByText('Superuser')).toBeInTheDocument();
  });

  it('should include navigation links to admin pages', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 1,
        username: 'admin',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    // Check that all the admin page links are present
    expect(screen.getByText('Manage Guilds')).toBeInTheDocument();
    expect(screen.getByText('Manage Scenarios')).toBeInTheDocument();
    expect(screen.getByText('Manage Teams')).toBeInTheDocument();
            expect(screen.getByText('Manage Characters')).toBeInTheDocument();
    expect(screen.getByText('Manage Toons')).toBeInTheDocument();
  });

  it('should include guild switcher component', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        user_id: 1,
        username: 'admin',
        is_superuser: true,
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      error: null,
      clearError: vi.fn(),
    });

    vi.mocked(useGuild).mockReturnValue({
      selectedGuild: null,
      availableGuilds: [],
      isLoading: false,
      error: null,
      selectGuild: vi.fn(),
      refreshGuilds: vi.fn(),
      clearError: vi.fn(),
    });

    renderWithProviders(<Settings />);

    expect(screen.getByTestId('guild-switcher')).toBeInTheDocument();
  });
}); 