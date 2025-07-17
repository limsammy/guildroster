import '@testing-library/jest-dom';
import { vi, beforeAll, afterAll } from 'vitest';

// Mock AbortSignal for React Router compatibility
class MockAbortSignal {
  aborted = false;
  
  static timeout() {
    return new MockAbortSignal();
  }
  
  addEventListener() {}
  removeEventListener() {}
}

// Mock global AbortSignal
global.AbortSignal = MockAbortSignal as any;

// Mock window.location for navigation tests
Object.defineProperty(window, 'location', {
  value: {
    href: '',
    assign: vi.fn(),
    replace: vi.fn(),
  },
  writable: true,
});

// Mock environment variables for testing
Object.defineProperty(import.meta, 'env', {
  value: {
    VITE_API_URL: 'http://localhost:8000',
    VITE_AUTH_TOKEN: '',
  },
  writable: true,
});

// Suppress console errors for expected test scenarios
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
}); 