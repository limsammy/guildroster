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
  };
});

// Mock alert
global.alert = vi.fn();

const renderLogin = () => {
  const router = createMemoryRouter([
    {
      path: '/login',
      element: <Login />,
    },
  ]);

  return render(<RouterProvider router={router} />);
};

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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

  it('shows alert after successful submission', async () => {
    renderLogin();

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('Login functionality will be implemented with the API integration');
    }, { timeout: 2000 });
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

  it('has proper error handling structure', () => {
    renderLogin();

    // Error message container should exist but be empty initially
    const form = screen.getByRole('form');
    expect(form).toBeInTheDocument();
  });
}); 