import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../app/contexts/AuthContext'

// Mock the AuthService with proper default export
vi.mock('../../app/api/auth', () => ({
  default: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    validateSession: vi.fn(),
  },
  AuthService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    validateSession: vi.fn(),
  },
}))

// Import the mocked module
import AuthService from '../../app/api/auth'

// Test component to access auth context
function TestComponent() {
  const { user, isAuthenticated, isLoading, error } = useAuth()
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!isAuthenticated) return <div>Not authenticated</div>
  
  return <div>Authenticated as: {user?.username}</div>
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(AuthService.isAuthenticated).mockResolvedValue(false)
    vi.mocked(AuthService.getCurrentUser).mockResolvedValue(null)
    vi.mocked(AuthService.validateSession).mockResolvedValue(false)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should show loading state initially', async () => {
    // Mock the initial check to take some time
    vi.mocked(AuthService.getCurrentUser).mockResolvedValue(null)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // The component should show loading initially, then not authenticated
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
  })

  it('should show not authenticated when no session', async () => {
    vi.mocked(AuthService.getCurrentUser).mockResolvedValue(null)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
  })

  it('should show authenticated user when session exists', async () => {
    const mockUser = {
      user_id: 1,
      username: 'testuser',
      is_superuser: false,
    }
    
    vi.mocked(AuthService.getCurrentUser).mockResolvedValue(mockUser)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Authenticated as: testuser')).toBeInTheDocument()
    })
  })

  it('should handle initialization error gracefully', async () => {
    vi.mocked(AuthService.getCurrentUser).mockRejectedValue(new Error('Test error'))
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
  })

  it('should handle login successfully', async () => {
    const mockUser = {
      user_id: 1,
      username: 'testuser',
      is_superuser: false,
    }
    
    const mockLoginResponse = {
      user_id: 1,
      username: 'testuser',
      is_superuser: false,
      access_token: 'test-token',
      token_type: 'bearer',
    }
    
    vi.mocked(AuthService.getCurrentUser).mockResolvedValue(null)
    vi.mocked(AuthService.login).mockResolvedValue(mockLoginResponse)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
  })

  it('should handle logout successfully', async () => {
    vi.mocked(AuthService.getCurrentUser).mockResolvedValue(null)
    vi.mocked(AuthService.logout).mockResolvedValue()
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
  })
}) 