import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Hero } from '../../app/components/sections/Hero';

// Mock React Router
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

// Mock AuthContext
const mockAuthContext = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  login: vi.fn(),
  logout: vi.fn(),
  error: null,
  clearError: vi.fn(),
};

vi.mock('../../app/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext,
}));

describe('Hero', () => {
  it('renders hero section with login button when not authenticated', () => {
    mockAuthContext.isAuthenticated = false;
    
    render(<Hero />);

    expect(screen.getByText('GuildRoster')).toBeInTheDocument();
    expect(screen.getByText('Command your guild\'s destiny with precision. Track attendance, manage rosters, and lead your team to victory in Azeroth\'s greatest challenges.')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('renders hero section with dashboard button when authenticated', () => {
    mockAuthContext.isAuthenticated = true;
    
    render(<Hero />);

    expect(screen.getByText('GuildRoster')).toBeInTheDocument();
    expect(screen.getByText('Command your guild\'s destiny with precision. Track attendance, manage rosters, and lead your team to victory in Azeroth\'s greatest challenges.')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /dashboard/i })).toBeInTheDocument();
  });

  it('has correct link destinations', () => {
    // Test login link
    mockAuthContext.isAuthenticated = false;
    const { rerender } = render(<Hero />);
    
    const loginLink = screen.getByRole('link', { name: /login/i });
    expect(loginLink).toHaveAttribute('href', '/login');

    // Test dashboard link
    mockAuthContext.isAuthenticated = true;
    rerender(<Hero />);
    
    const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
    expect(dashboardLink).toHaveAttribute('href', '/dashboard');
  });

  it('displays the correct tagline', () => {
    render(<Hero />);
    
    expect(screen.getByText('Command your guild\'s destiny with precision. Track attendance, manage rosters, and lead your team to victory in Azeroth\'s greatest challenges.')).toBeInTheDocument();
  });

  it('has proper styling classes', () => {
    render(<Hero />);
    
    const heroSection = screen.getByText('GuildRoster').closest('section');
    expect(heroSection).toHaveClass('relative', 'min-h-screen', 'flex', 'items-center', 'justify-center', 'overflow-hidden');
  });
}); 