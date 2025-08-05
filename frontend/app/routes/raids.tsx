import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { RaidService } from '../api/raids';
import type { Raid } from '../api/types';
import { RaidForm } from '../components/ui/RaidForm';
import { TeamService } from '../api/teams';
import { ScenarioService } from '../api/scenarios';
import type { Team } from '../api/types';
import type { Scenario } from '../api/types';
import { exportJson } from '../utils/exportJson';
import { Footer } from '../components/layout/Footer';

export function meta() {
  return [
    { title: 'Raids - GuildRoster' },
    { name: 'description', content: 'Manage raids and their scheduling.' },
  ];
}

export default function Raids() {
  const { user } = useAuth();
  const [raids, setRaids] = useState<Raid[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingRaid, setEditingRaid] = useState<Raid | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [raidsData, teamsData, scenariosData] = await Promise.all([
          RaidService.getRaids(),
          TeamService.getTeams(),
          ScenarioService.getScenarios(),
        ]);
        setRaids(raidsData);
        setTeams(teamsData);
        setScenarios(scenariosData);
      } catch (err: any) {
        setError(err.message || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Helper function to get team name by ID
  const getTeamName = (teamId: number) => {
    const team = teams.find(t => t.id === teamId);
    return team ? team.name : `Team #${teamId}`;
  };

  // Helper function to get scenario display name
  const getScenarioDisplayName = (raid: Raid) => {
    return `${raid.scenario_name} (${raid.scenario_difficulty}, ${raid.scenario_size}-man)`;
  };

  // Helper function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Helper function to check if raid is in the past
  const isPastRaid = (dateString: string) => {
    return new Date(dateString) < new Date();
  };

  // Reload raids from the API
  const reloadRaids = async () => {
    try {
      const updatedRaids = await RaidService.getRaids();
      setRaids(updatedRaids);
    } catch (err: any) {
      setError(err.message || 'Failed to reload raids');
    }
  };

  // Fetch teams and scenarios when showing the form
  const openAddForm = async () => {
    setFormLoading(true);
    setFormError(null);
    try {
      const [teamsData, scenariosData] = await Promise.all([
        TeamService.getTeams(),
        ScenarioService.getScenarios(),
      ]);
      setTeams(teamsData);
      setScenarios(scenariosData);
      setShowAddForm(true);
    } catch (err: any) {
      setFormError(err.message || 'Failed to load form data');
    } finally {
      setFormLoading(false);
    }
  };

  const openEditForm = async (raid: Raid) => {
    setFormLoading(true);
    setFormError(null);
    try {
      const [teamsData, scenariosData] = await Promise.all([
        TeamService.getTeams(),
        ScenarioService.getScenarios(),
      ]);
      setTeams(teamsData);
      setScenarios(scenariosData);
      setEditingRaid(raid);
    } catch (err: any) {
      setFormError(err.message || 'Failed to load form data');
    } finally {
      setFormLoading(false);
    }
  };

  const handleAddRaid = async (values: { warcraftlogs_url: string; team_id: number; scenario_name: string; scenario_difficulty: string; scenario_size: string; scheduled_at: string; updated_attendance?: any[] }) => {
    setFormLoading(true);
    setFormError(null);
    try {
      await RaidService.createRaid({
        scheduled_at: values.scheduled_at,
        team_id: values.team_id,
        scenario_name: values.scenario_name,
        scenario_difficulty: values.scenario_difficulty,
        scenario_size: values.scenario_size,
        warcraftlogs_url: values.warcraftlogs_url || undefined,
        updated_attendance: values.updated_attendance,
      });
      setShowAddForm(false);
      await reloadRaids();
    } catch (err: any) {
      setFormError(err.message || 'Failed to add raid');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditRaid = async (values: { warcraftlogs_url: string; team_id: number; scenario_name: string; scenario_difficulty: string; scenario_size: string; scheduled_at: string }) => {
    if (!editingRaid) return;
    setFormLoading(true);
    setFormError(null);
    try {
      await RaidService.updateRaid(editingRaid.id, {
        team_id: values.team_id,
        scenario_name: values.scenario_name,
        scenario_difficulty: values.scenario_difficulty,
        scenario_size: values.scenario_size,
        scheduled_at: values.scheduled_at,
        warcraftlogs_url: values.warcraftlogs_url || undefined,
      });
      setEditingRaid(null);
      await reloadRaids();
    } catch (err: any) {
      setFormError(err.message || 'Failed to update raid');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteRaid = async (raidId: number) => {
    if (!confirm('Are you sure you want to delete this raid? This action cannot be undone.')) return;
    try {
      await RaidService.deleteRaid(raidId);
      await reloadRaids();
    } catch (err: any) {
      setError(err.message || 'Failed to delete raid');
    }
  };

  const handleCancelForm = () => {
    setShowAddForm(false);
    setEditingRaid(null);
    setFormError(null);
  };

  // Filter raids based on search and date filter
  const filteredRaids = raids.filter(raid => {
    const matchesSearch = searchTerm === '' || 
      raid.id.toString().includes(searchTerm) ||
      getTeamName(raid.team_id).toLowerCase().includes(searchTerm.toLowerCase()) ||
      getScenarioDisplayName(raid).toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDate = dateFilter === '' || 
      raid.scheduled_at.startsWith(dateFilter);
    
    return matchesSearch && matchesDate;
  });

  // Sort raids by scheduled date (newest first)
  const sortedRaids = [...filteredRaids].sort((a, b) => 
    new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime()
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading raids...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Raids</h2>
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
                  <span className="text-slate-300">Raids</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Raids</h1>
                <p className="text-slate-300 mt-1">Manage your raids and their scheduling</p>
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" onClick={() => exportJson(raids, 'raids.json')}>
                  Export as JSON
                </Button>
                <Link to="/dashboard">
                  <Button variant="secondary">Dashboard</Button>
                </Link>
                <Button variant="primary" onClick={openAddForm}>
                  Add Raid
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Search and Filter Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="search" className="block text-sm font-medium text-slate-300 mb-2">
                  Search Raids
                </label>
                <input
                  id="search"
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder="Search by ID, team, or scenario..."
                />
              </div>
              <div>
                <label htmlFor="date-filter" className="block text-sm font-medium text-slate-300 mb-2">
                  Filter by Date
                </label>
                <input
                  id="date-filter"
                  type="date"
                  value={dateFilter}
                  onChange={e => setDateFilter(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-end">
                <Button 
                  variant="secondary" 
                  onClick={() => {
                    setSearchTerm('');
                    setDateFilter('');
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </Card>

          {/* Raids List */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Raids</h2>
              <div className="text-sm text-slate-400">
                {sortedRaids.length} of {raids.length} raids
              </div>
            </div>

            {sortedRaids.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-slate-400 text-6xl mb-4">🗡️</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {searchTerm || dateFilter ? 'No raids found' : 'No raids yet'}
                </h3>
                <p className="text-slate-400 mb-6">
                  {searchTerm || dateFilter 
                    ? 'Try adjusting your search terms or filters' 
                    : 'Get started by adding your first raid'
                  }
                </p>
                {!searchTerm && !dateFilter && (
                  <Button variant="primary" onClick={openAddForm}>
                    Add First Raid
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {sortedRaids.map(raid => (
                  <div
                    key={raid.id}
                    className={`flex items-center justify-between p-4 rounded-lg border transition-colors ${
                      isPastRaid(raid.scheduled_at)
                        ? 'bg-slate-800/30 border-slate-700/30'
                        : 'bg-slate-800/50 border-slate-700/50 hover:border-slate-600/50'
                    }`}
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-2">
                        <span className="text-white font-medium">Raid #{raid.id}</span>
                        {isPastRaid(raid.scheduled_at) && (
                          <span className="px-2 py-1 text-xs bg-slate-700 text-slate-300 rounded">
                            Past
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-400">
                        <div>
                          <span className="font-medium text-slate-300">Scheduled:</span>
                          <br />
                          {formatDate(raid.scheduled_at)}
                        </div>
                        <div>
                          <span className="font-medium text-slate-300">Team:</span>
                          <br />
                          {getTeamName(raid.team_id)}
                        </div>
                        <div>
                          <span className="font-medium text-slate-300">Scenario:</span>
                          <br />
                          {getScenarioDisplayName(raid)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => openEditForm(raid)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteRaid(raid.id)}
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

      {/* Add/Edit Form Modal */}
      {(showAddForm || editingRaid) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-2 sm:p-4 z-50">
          <div className="w-full max-w-md mx-auto">
            <RaidForm
              teams={teams}
              scenarios={scenarios}
              loading={formLoading}
              error={formError}
              onSubmit={showAddForm ? handleAddRaid : handleEditRaid}
              onCancel={handleCancelForm}
              isEditing={!!editingRaid}
              initialValues={editingRaid ? {
                team_id: editingRaid.team_id,
                scenario_name: editingRaid.scenario_name,
                scenario_difficulty: editingRaid.scenario_difficulty,
                scenario_size: editingRaid.scenario_size,
                scheduled_at: editingRaid.scheduled_at.slice(0, 16), // Convert ISO string to datetime-local format
                warcraftlogs_url: editingRaid.warcraftlogs_url || '',
              } : {}}
            />
          </div>
        </div>
      )}
      <Footer />
    </div>
  );
} 