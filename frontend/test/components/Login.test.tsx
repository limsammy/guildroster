import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { createMemoryRouter, RouterProvider } from 'react-router';
import Login from '../../app/routes/login';

// Mock React Router
const mockNavigate = vi.fn();

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router');
  return {
    ...actual,
    Link: ({ to, children, ...props }: any) => (
      <a href={to} {...props}>
        {children}
      </a>
    ),
    useNavigate: () => mockNavigate,
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

// Mock AuthContext
const mockLogin = vi.fn();
const mockAuthContext: {
  user: { user_id: number; username: string; is_superuser: boolean } | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: typeof mockLogin;
  logout: () => void;
  error: string | null;
  clearError: () => void;
} = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  login: mockLogin,
  logout: vi.fn(),
  error: null,
  clearError: vi.fn(),
};

vi.mock('../../app/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext,
}));

const renderLogin = () => {
  const router = createMemoryRouter([
    {
      path: '/',
      element: <div>Home</div>,
    },
    {
      path: '/login',
      element: <Login />,
    },
  ], {
    initialEntries: ['/login'],
    initialIndex: 1,
  });

  return render(<RouterProvider router={router} />);
};

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    // Reset mock auth context
    mockAuthContext.user = null;
    mockAuthContext.isAuthenticated = false;
    mockAuthContext.isLoading = false;
    mockAuthContext.error = null;
  });

  it('renders login form with all elements', () => {
    renderLogin();

    expect(screen.getByText('GuildRoster')).toBeInTheDocument();
    expect(screen.getByText('Sign in to your account')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
    expect(screen.getByText('Remember me')).toBeInTheDocument();
  });

  it('allows user to input username and password', () => {
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });

    expect(usernameInput).toHaveValue('testuser');
    expect(passwordInput).toHaveValue('testpass');
  });

  it('shows loading state when form is submitted', async () => {
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);

    expect(screen.getByRole('button', { name: 'Signing in...' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Signing in...' })).toBeDisabled();
  });

  it('handles form submission and calls login function', async () => {
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);

    // Wait for the loading state
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Signing in...' })).toBeInTheDocument();
    });

    // Wait for the form submission to complete
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpass',
      });
    });
  });

  it('requires username and password fields', () => {
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');

    expect(usernameInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });

  it('has proper form validation', () => {
    renderLogin();

    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    fireEvent.click(submitButton);

    // Form should not submit without required fields
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('has accessible form labels and inputs', () => {
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');

    expect(usernameInput).toHaveAttribute('id', 'username');
    expect(passwordInput).toHaveAttribute('id', 'password');
    expect(usernameInput).toHaveAttribute('name', 'username');
    expect(passwordInput).toHaveAttribute('name', 'password');
  });

  it('has proper focus styles and accessibility', () => {
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');

    expect(usernameInput).toHaveAttribute('type', 'text');
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('includes remember me checkbox', () => {
    renderLogin();

    const rememberCheckbox = screen.getByLabelText('Remember me');
    expect(rememberCheckbox).toBeInTheDocument();
    expect(rememberCheckbox).toHaveAttribute('type', 'checkbox');
  });

  it('has proper form structure', () => {
    renderLogin();

    // Form should be present with proper role
    const form = screen.getByRole('form');
    expect(form).toBeInTheDocument();
    
    // Form should contain all required elements
    expect(form).toContainElement(screen.getByLabelText('Username'));
    expect(form).toContainElement(screen.getByLabelText('Password'));
    expect(form).toContainElement(screen.getByRole('button', { name: 'Sign in' }));
  });

  it('shows loading state when checking authentication', () => {
    mockAuthContext.isLoading = true;
    
    renderLogin();

    expect(screen.getByText('Checking authentication...')).toBeInTheDocument();
  });

  it('shows already authenticated message when user is authenticated', () => {
    mockAuthContext.isAuthenticated = true;
    mockAuthContext.user = { user_id: 1, username: 'testuser', is_superuser: false };
    
    renderLogin();

    expect(screen.getByText('You are already logged in!')).toBeInTheDocument();
    expect(screen.getByText('Redirecting to dashboard...')).toBeInTheDocument();
    expect(screen.getByText('You are already authenticated and will be redirected shortly.')).toBeInTheDocument();
  });

  it('does not show login form when already authenticated', () => {
    mockAuthContext.isAuthenticated = true;
    mockAuthContext.user = { user_id: 1, username: 'testuser', is_superuser: false };
    
    renderLogin();

    expect(screen.queryByLabelText('Username')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Password')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Sign in' })).not.toBeInTheDocument();
  });

  it('shows error message when login fails', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid credentials'));
    
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  it('shows auth context error when present', () => {
    mockAuthContext.error = 'Authentication error from context';
    
    renderLogin();

    expect(screen.getByText('Authentication error from context')).toBeInTheDocument();
  });
}); 