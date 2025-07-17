import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { GuildService } from '../api/guilds';
import type { Guild } from '../api/types';

export function meta() {
  return [
    { title: 'Guilds - GuildRoster' },
    { name: 'description', content: 'Manage guilds and their settings.' },
  ];
}

export default function Guilds() {
  const { user } = useAuth();
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGuilds = async () => {
      try {
        setLoading(true);
        setError(null);
        const guildsData = await GuildService.getGuilds();
        setGuilds(guildsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load guilds');
      } finally {
        setLoading(false);
      }
    };
    fetchGuilds();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading guilds...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Guilds</h2>
          <p className="text-slate-300 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="bg-slate-800/60 border-b border-slate-600/50">
        <Container>
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <nav className="flex items-center space-x-2 text-sm text-slate-400 mb-2">
                  <Link to="/dashboard" className="hover:text-amber-400">Dashboard</Link>
                  <span>/</span>
                  <span className="text-slate-300">Guilds</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Guilds</h1>
                <p className="text-slate-300 mt-1">Manage your guilds and their settings</p>
              </div>
              <div className="flex gap-3">
                <Link to="/dashboard">
                  <Button variant="secondary">Dashboard</Button>
                </Link>
                <Button variant="primary">Add Guild</Button>
              </div>
            </div>
          </div>
        </Container>
      </div>
      <Container>
        <div className="py-8">
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Guild List</h2>
              <div className="text-slate-400">{guilds.length} guild{guilds.length !== 1 ? 's' : ''}</div>
            </div>
            {guilds.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚔️</div>
                <h3 className="text-xl font-semibold text-white mb-2">No Guilds Found</h3>
                <p className="text-slate-300 mb-6">Get started by creating your first guild</p>
                <Button variant="primary">Create First Guild</Button>
              </div>
            ) : (
              <div className="space-y-4">
                {guilds.map((guild) => (
                  <div key={guild.id} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg border border-slate-600/30 hover:border-slate-500/50 transition-colors">
                    <div>
                      <h3 className="font-semibold text-white">{guild.name}</h3>
                      <p className="text-sm text-slate-300">{guild.realm} • {guild.faction}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button size="sm" variant="secondary">Edit</Button>
                      <Button size="sm" variant="danger">Delete</Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </Container>
    </div>
  );
} 