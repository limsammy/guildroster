import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
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

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should check if user is authenticated', () => {
    localStorageMock.getItem.mockReturnValue('test-token')
    expect(AuthService.isAuthenticated()).toBe(true)

    localStorageMock.getItem.mockReturnValue(null)
    expect(AuthService.isAuthenticated()).toBe(false)
  })

  it('should get stored token', () => {
    localStorageMock.getItem.mockReturnValue('test-token')
    expect(AuthService.getToken()).toBe('test-token')
  })

  it('should logout and remove token', async () => {
    await AuthService.logout()
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
  })
}) 