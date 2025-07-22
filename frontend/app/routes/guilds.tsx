import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container, GuildForm } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { useGuild } from '../contexts/GuildContext';
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
  const { refreshGuilds: refreshGuildContext } = useGuild();
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingGuild, setEditingGuild] = useState<Guild | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

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

  // Add this function to reload guilds from the API
  const reloadGuilds = async () => {
    const updatedGuilds = await GuildService.getGuilds();
    setGuilds(updatedGuilds);
    // Also refresh the GuildContext so other components (like GuildSwitcher) update
    await refreshGuildContext();
  };

  const handleAddGuild = async (values: { name: string }) => {
    if (!user) {
      setFormError('User not authenticated');
      return;
    }
    
    try {
      setFormLoading(true);
      setFormError(null);
      await GuildService.createGuild(values);
      await reloadGuilds();
      setShowAddForm(false);
    } catch (err: any) {
      console.error('Error creating guild:', err);
      setFormError(err.message || 'Failed to create guild');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditGuild = async (values: { name: string }) => {
    if (!editingGuild) return;
    try {
      setFormLoading(true);
      setFormError(null);
      await GuildService.updateGuild(editingGuild.id, values);
      await reloadGuilds();
      setEditingGuild(null);
    } catch (err: any) {
      console.error('Error updating guild:', err);
      setFormError(err.message || 'Failed to update guild');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteGuild = async (guildId: number) => {
    if (!confirm('Are you sure you want to delete this guild? This action cannot be undone.')) return;
    
    try {
      await GuildService.deleteGuild(guildId);
      await reloadGuilds();
    } catch (err: any) {
      console.error('Error deleting guild:', err);
      alert('Failed to delete guild: ' + (err.message || 'Unknown error'));
    }
  };

  const handleCancelForm = () => {
    setShowAddForm(false);
    setEditingGuild(null);
    setFormError(null);
  };

  // Filter guilds based on search
  const filteredGuilds = guilds.filter(guild => {
    const matchesSearch = guild.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Calculate statistics
  const totalGuilds = guilds.length;

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
      {/* Header */}
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
                <Button variant="primary" onClick={() => setShowAddForm(true)}>
                  Add Guild
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 gap-6 mb-8">
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-amber-400 mb-2">{totalGuilds}</div>
              <div className="text-slate-300">Total Guilds</div>
            </Card>
          </div>

          {/* Search Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="search" className="block text-sm font-medium text-slate-300 mb-2">
                  Search Guilds
                </label>
                <input
                  id="search"
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder="Search by guild name..."
                />
              </div>
              <div className="flex items-end">
                <Button 
                  variant="secondary" 
                  onClick={() => setSearchTerm('')}
                  className="w-full"
                >
                  Clear Search
                </Button>
              </div>
            </div>
          </Card>

          {/* Guilds List */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Guild List</h2>
              <div className="text-slate-400">
                {filteredGuilds.length} of {guilds.length} guild{filteredGuilds.length !== 1 ? 's' : ''}
              </div>
            </div>

            {filteredGuilds.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚔️</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {guilds.length === 0 ? 'No Guilds Found' : 'No Guilds Match Search'}
                </h3>
                <p className="text-slate-300 mb-6">
                  {guilds.length === 0 
                    ? 'Get started by creating your first guild'
                    : 'Try adjusting your search criteria'
                  }
                </p>
                {guilds.length === 0 && (
                  <Button variant="primary" onClick={() => setShowAddForm(true)}>
                    Create First Guild
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredGuilds.map((guild) => (
                  <div key={guild.id} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg border border-slate-600/30 hover:border-slate-500/50 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                      <div>
                        <h3 className="font-semibold text-white">{guild.name}</h3>
                        <p className="text-sm text-slate-300">Guild ID: {guild.id}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button 
                        size="sm" 
                        variant="secondary"
                        onClick={() => setEditingGuild(guild)}
                      >
                        Edit
                      </Button>
                      <Button 
                        size="sm" 
                        variant="danger"
                        onClick={() => handleDeleteGuild(guild.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </Container>

      {/* Add/Edit Modal */}
      {(showAddForm || editingGuild) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" data-testid="guild-form-modal">
          <div className="w-full max-w-md">
            <GuildForm
              mode={editingGuild ? 'edit' : 'add'}
              initialValues={editingGuild || {}}
              loading={formLoading}
              error={formError}
              onSubmit={editingGuild ? handleEditGuild : handleAddGuild}
              onCancel={handleCancelForm}
            />
          </div>
        </div>
      )}
    </div>
  );
} 