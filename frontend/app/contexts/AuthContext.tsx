import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import AuthService from '../api/auth';
import type { LoginCredentials, LoginResponse, UserInfo } from '../api/auth';

interface AuthContextType {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state on app load
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check if user is authenticated by fetching user info from session
        const currentUser = await AuthService.getCurrentUser();
        
        if (currentUser) {
          setUser(currentUser);
        } else {
          // No user found - this is a normal state, not an error
          setUser(null);
        }
      } catch (err) {
        console.error('Unexpected error initializing auth:', err);
        // Set user to null on any unexpected error
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      setIsLoading(true);
      setError(null);
      
      await AuthService.login(credentials);
      
      // Get user info from server after successful login
      const currentUser = await AuthService.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
      }
    } catch (err: any) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await AuthService.logout();
    } catch (err) {
      console.error('AuthContext: Logout error:', err);
    } finally {
      setUser(null);
      setError(null);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    error,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 