/**
 * Storage utilities for development and debugging
 */

/**
 * Clear all localStorage data
 * This is useful for development and testing purposes
 */
export const clearLocalStorage = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.clear();
    console.log('localStorage cleared successfully');
  }
};

/**
 * Clear specific localStorage items
 * @param keys - Array of keys to remove from localStorage
 */
export const clearLocalStorageItems = (keys: string[]): void => {
  if (typeof window !== 'undefined') {
    keys.forEach(key => {
      localStorage.removeItem(key);
    });
    console.log(`Cleared localStorage items: ${keys.join(', ')}`);
  }
};

/**
 * Get all localStorage keys
 * @returns Array of localStorage keys
 */
export const getLocalStorageKeys = (): string[] => {
  if (typeof window !== 'undefined') {
    return Object.keys(localStorage);
  }
  return [];
};

/**
 * Log all localStorage data for debugging
 */
export const logLocalStorage = (): void => {
  if (typeof window !== 'undefined') {
    const keys = getLocalStorageKeys();
    if (keys.length === 0) {
      console.log('localStorage is empty');
      return;
    }
    
    console.log('localStorage contents:');
    keys.forEach(key => {
      const value = localStorage.getItem(key);
      console.log(`  ${key}: ${value}`);
    });
  }
}; 