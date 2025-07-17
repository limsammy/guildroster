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
    validateToken: vi.fn(),
  },
  AuthService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    validateToken: vi.fn(),
  },
}))

// Import the mocked module
import AuthService from '../../app/api/auth'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

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
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(false)
    vi.mocked(AuthService.getCurrentUser).mockReturnValue(null)
    vi.mocked(AuthService.validateToken).mockResolvedValue(false)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should show loading state initially', async () => {
    // Mock the initial check to take some time
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(false)
    
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

  it('should show not authenticated when no token', async () => {
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(false)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
  })

  it('should show authenticated user when token exists', async () => {
    const mockUser = {
      user_id: 1,
      username: 'testuser',
      is_superuser: false,
    }
    
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(true)
    vi.mocked(AuthService.getCurrentUser).mockReturnValue(mockUser)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Authenticated as: testuser')).toBeInTheDocument()
    })
  })

  it('should show authenticated user when token exists but no user info', async () => {
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(true)
    vi.mocked(AuthService.getCurrentUser).mockReturnValue(null)
    vi.mocked(AuthService.validateToken).mockResolvedValue(true)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Authenticated as: API User')).toBeInTheDocument()
    })
  })

  it('should show not authenticated when token validation fails', async () => {
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(true)
    vi.mocked(AuthService.getCurrentUser).mockReturnValue(null)
    vi.mocked(AuthService.validateToken).mockResolvedValue(false)
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
  })

  it('should handle initialization error gracefully', async () => {
    vi.mocked(AuthService.isAuthenticated).mockImplementation(() => {
      throw new Error('Test error')
    })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument()
    })
    
    // Should have called logout due to error
    expect(AuthService.logout).toHaveBeenCalled()
  })
}) 