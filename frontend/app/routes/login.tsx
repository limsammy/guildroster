import React, { useState, useEffect } from 'react';
import { Button, Card, Container } from "../components/ui";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../contexts/AuthContext";

export function meta() {
  return [
    { title: "Login - GuildRoster" },
    { name: "description", content: "Login to GuildRoster to manage your guild's roster and track attendance." },
  ];
}

export default function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is already authenticated
  useEffect(() => {
    const token = localStorage.getItem('auth_token') || import.meta.env.VITE_AUTH_TOKEN;
    if (token) {
      setIsAuthenticated(true);
      // Redirect after a short delay to show the message
      setTimeout(() => {
        navigate('/');
      }, 2000);
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // For now, simulate a successful login
      // In a real implementation, you would call the API here
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store a dummy token to simulate authentication
      localStorage.setItem('auth_token', 'dummy-token');
      localStorage.setItem('user_info', JSON.stringify({
        user_id: 1,
        username: formData.username,
        is_superuser: false,
      }));
      
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Container maxWidth="sm">
        <div className="text-center mb-8">
          <Link to="/" className="inline-block">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent mb-2">
              GuildRoster
            </h1>
          </Link>
          {isAuthenticated ? (
            <div className="space-y-4">
              <p className="text-green-400 text-lg">You are already logged in!</p>
              <p className="text-slate-300">Redirecting to home page...</p>
            </div>
          ) : (
            <p className="text-slate-300">Sign in to your account</p>
          )}
        </div>

        {isAuthenticated ? (
          <Card variant="elevated" className="max-w-md mx-auto text-center">
            <div className="py-8">
              <div className="text-6xl mb-4">✅</div>
              <p className="text-slate-300">You are already authenticated and will be redirected shortly.</p>
            </div>
          </Card>
        ) : (
          <Card variant="elevated" className="max-w-md mx-auto">
            <form onSubmit={handleSubmit} className="space-y-6" role="form">
              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              )}

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-colors"
                  placeholder="Enter your username"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-colors"
                  placeholder="Enter your password"
                />
              </div>

              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-amber-500 focus:ring-amber-500 border-slate-600 rounded bg-slate-800"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-300">
                  Remember me
                </label>
              </div>

              <Button
                type="submit"
                size="lg"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>
          </Card>
        )}
      </Container>
    </div>
  );
} 