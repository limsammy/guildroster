import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { useAuth } from '../../contexts/AuthContext';
import { AuthService } from '../../api/auth';
import type { UserInfo } from '../../api/auth';

export const Navigation: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<UserInfo | null>(null);
  const { isAuthenticated, logout } = useAuth();

  useEffect(() => {
    const loadUserInfo = async () => {
      if (isAuthenticated) {
        try {
          const user = await AuthService.getCurrentUser();
          setCurrentUser(user);
        } catch (error) {
          console.error('Failed to load user info:', error);
        }
      } else {
        setCurrentUser(null);
      }
    };

    loadUserInfo();
  }, [isAuthenticated]);

  const handleLogout = async () => {
    try {
      await logout();
      setIsMenuOpen(false);
    } catch (error) {
      console.error('Navigation: Logout failed:', error);
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                GuildRoster
              </h1>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {isAuthenticated ? (
              <>
                <Link 
                  to="/dashboard"
                  className="text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-800/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-900"
                >
                  Dashboard
                </Link>
                {currentUser?.is_superuser && (
                  <Link 
                    to="/invites"
                    className="text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-800/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-900"
                  >
                    Invites
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-800/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-900"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link 
                to="/login"
                className="text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-800/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-900"
              >
                Login
              </Link>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-slate-300 hover:text-white focus:outline-none focus:text-white"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-slate-800/90 backdrop-blur-md border-t border-slate-700/50">
              <div className="pt-4 space-y-2">
                {isAuthenticated ? (
                  <>
                    <Link 
                      to="/dashboard" 
                      onClick={() => setIsMenuOpen(false)}
                      className="block w-full text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-700/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-800"
                    >
                      Dashboard
                    </Link>
                    {currentUser?.is_superuser && (
                      <Link 
                        to="/invites" 
                        onClick={() => setIsMenuOpen(false)}
                        className="block w-full text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-700/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-800"
                      >
                        Invites
                      </Link>
                    )}
                    <button
                      onClick={handleLogout}
                      className="block w-full text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-700/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-800"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <Link 
                    to="/login" 
                    onClick={() => setIsMenuOpen(false)}
                    className="block w-full text-slate-300 hover:text-slate-100 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-slate-700/80 border border-slate-600/30 hover:border-slate-500/50 focus:outline-none focus:ring-2 focus:ring-slate-500/50 focus:ring-offset-2 focus:ring-offset-slate-800"
                  >
                    Login
                  </Link>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}; 