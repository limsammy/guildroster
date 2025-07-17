import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import AuthService from '../api/auth';
import type { LoginCredentials, LoginResponse } from '../api/auth';

interface User {
  user_id: number;
  username: string;
  is_superuser: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state on app load
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check if we have a token (either from localStorage or environment)
        if (AuthService.isAuthenticated()) {
          const currentUser = AuthService.getCurrentUser();
          
          if (currentUser) {
            // We have both token and user info
            setUser(currentUser);
          } else {
            // We have a token but no user info (likely environment token)
            // Try to validate the token with the backend
            const isValid = await AuthService.validateToken();
            if (isValid) {
              // For environment tokens, create a default user
              setUser({
                user_id: 0,
                username: 'API User',
                is_superuser: true,
              });
            } else {
              // Token is invalid, clear it
              AuthService.logout();
            }
          }
        }
      } catch (err) {
        console.error('Error initializing auth:', err);
        AuthService.logout();
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
      
      const response = await AuthService.login(credentials);
      setUser({
        user_id: response.user_id,
        username: response.username,
        is_superuser: response.is_superuser,
      });
    } catch (err: any) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    AuthService.logout();
    setUser(null);
    setError(null);
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