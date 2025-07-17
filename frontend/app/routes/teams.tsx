import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container, TeamForm } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { TeamService } from '../api/teams';
import { GuildService } from '../api/guilds';
import type { Team, Guild } from '../api/types';

export function meta() {
  return [
    { title: 'Teams - GuildRoster' },
    { name: 'description', content: 'Manage teams and their assignments.' },
  ];
}

export default function Teams() {
  const { user } = useAuth();
  const [teams, setTeams] = useState<Team[]>([]);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGuild, setSelectedGuild] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTeam, setEditingTeam] = useState<Team | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [teamsData, guildsData] = await Promise.all([
          TeamService.getTeams(),
          GuildService.getGuilds(),
        ]);
        setTeams(teamsData);
        setGuilds(guildsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load teams');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAddTeam = async (values: { name: string; guild_id: number }) => {
    if (!user) {
      setFormError('User not authenticated');
      return;
    }
    
    try {
      setFormLoading(true);
      setFormError(null);
      const newTeam = await TeamService.createTeam({
        ...values,
        created_by: user.user_id,
      });
      setTeams(prev => [...prev, newTeam]);
      setShowAddForm(false);
    } catch (err: any) {
      console.error('Error creating team:', err);
      setFormError(err.message || 'Failed to create team');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditTeam = async (values: { name: string; guild_id: number }) => {
    if (!editingTeam) return;
    try {
      setFormLoading(true);
      setFormError(null);
      const updatedTeam = await TeamService.updateTeam(editingTeam.id, values);
      setTeams(prev => prev.map(t => t.id === editingTeam.id ? updatedTeam : t));
      setEditingTeam(null);
    } catch (err: any) {
      console.error('Error updating team:', err);
      setFormError(err.message || 'Failed to update team');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteTeam = async (teamId: number) => {
    if (!confirm('Are you sure you want to delete this team? This action cannot be undone.')) return;
    
    try {
      await TeamService.deleteTeam(teamId);
      setTeams(prev => prev.filter(t => t.id !== teamId));
    } catch (err: any) {
      console.error('Error deleting team:', err);
      alert('Failed to delete team: ' + (err.message || 'Unknown error'));
    }
  };

  const handleCancelForm = () => {
    setShowAddForm(false);
    setEditingTeam(null);
    setFormError(null);
  };

  // Filter teams based on search and guild filter
  const filteredTeams = teams.filter(team => {
    const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesGuild = selectedGuild === '' || team.guild_id === Number(selectedGuild);
    
    return matchesSearch && matchesGuild;
  });

  // Calculate statistics
  const totalTeams = teams.length;
  const teamsByGuild = guilds.map(guild => ({
    guild,
    count: teams.filter(team => team.guild_id === guild.id).length
  }));

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading teams...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Teams</h2>
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
                  <span className="text-slate-300">Teams</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Teams</h1>
                <p className="text-slate-300 mt-1">Manage your teams and their assignments</p>
              </div>
              <div className="flex gap-3">
                <Link to="/dashboard">
                  <Button variant="secondary">Dashboard</Button>
                </Link>
                <Button variant="primary" onClick={() => setShowAddForm(true)}>
                  Add Team
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-amber-400 mb-2">{totalTeams}</div>
              <div className="text-slate-300">Total Teams</div>
            </Card>
            {teamsByGuild.slice(0, 2).map(({ guild, count }) => (
              <Card key={guild.id} variant="elevated" className="text-center p-6">
                <div className="text-3xl font-bold text-blue-400 mb-2">{count}</div>
                <div className="text-slate-300">{guild.name} Teams</div>
              </Card>
            ))}
          </div>

          {/* Search and Filter Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="search" className="block text-sm font-medium text-slate-300 mb-2">
                  Search Teams
                </label>
                <input
                  id="search"
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder="Search by team name..."
                />
              </div>
              <div>
                <label htmlFor="guild-filter" className="block text-sm font-medium text-slate-300 mb-2">
                  Filter by Guild
                </label>
                <select
                  id="guild-filter"
                  value={selectedGuild}
                  onChange={e => setSelectedGuild(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  <option value="">All Guilds</option>
                  {guilds.map(guild => (
                    <option key={guild.id} value={guild.id}>{guild.name}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <Button 
                  variant="secondary" 
                  onClick={() => { setSearchTerm(''); setSelectedGuild(''); }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </Card>

          {/* Teams List */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Team List</h2>
              <div className="text-slate-400">
                {filteredTeams.length} of {teams.length} team{filteredTeams.length !== 1 ? 's' : ''}
              </div>
            </div>

            {filteredTeams.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚔️</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {teams.length === 0 ? 'No Teams Found' : 'No Teams Match Filters'}
                </h3>
                <p className="text-slate-300 mb-6">
                  {teams.length === 0 
                    ? 'Get started by creating your first team'
                    : 'Try adjusting your search or filter criteria'
                  }
                </p>
                {teams.length === 0 && (
                  <Button variant="primary" onClick={() => setShowAddForm(true)}>
                    Create First Team
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredTeams.map((team) => {
                  const guild = guilds.find(g => g.id === team.guild_id);
                  return (
                    <div key={team.id} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg border border-slate-600/30 hover:border-slate-500/50 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                        <div>
                          <h3 className="font-semibold text-white">{team.name}</h3>
                          <p className="text-sm text-slate-300">
                            {guild ? guild.name : 'Unknown Guild'} • Team ID: {team.id}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button 
                          size="sm" 
                          variant="secondary"
                          onClick={() => setEditingTeam(team)}
                        >
                          Edit
                        </Button>
                        <Button 
                          size="sm" 
                          variant="danger"
                          onClick={() => handleDeleteTeam(team.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>
      </Container>

      {/* Add/Edit Modal */}
      {(showAddForm || editingTeam) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" data-testid="team-form-modal">
          <div className="w-full max-w-md">
            <TeamForm
              mode={editingTeam ? 'edit' : 'add'}
              initialValues={editingTeam || {}}
              guilds={guilds}
              loading={formLoading}
              error={formError}
              onSubmit={editingTeam ? handleEditTeam : handleAddTeam}
              onCancel={handleCancelForm}
            />
          </div>
        </div>
      )}
    </div>
  );
} 