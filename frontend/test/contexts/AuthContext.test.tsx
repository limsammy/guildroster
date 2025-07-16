import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../app/contexts/AuthContext'

// Mock the AuthService
vi.mock('../../app/api/auth', () => ({
  AuthService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
  },
}))

// Import the mocked module
import { AuthService } from '../../app/api/auth'

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
      id: 1,
      username: 'testuser',
      is_superuser: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }
    
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(true)
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

  it('should show error when getCurrentUser fails', async () => {
    vi.mocked(AuthService.isAuthenticated).mockReturnValue(true)
    vi.mocked(AuthService.getCurrentUser).mockRejectedValue(new Error('API Error'))
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Error: Failed to get user info')).toBeInTheDocument()
    })
  })
}) 