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
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingRaid, setEditingRaid] = useState<Raid | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRaids = async () => {
      try {
        setLoading(true);
        setError(null);
        const raidsData = await RaidService.getRaids();
        setRaids(raidsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load raids');
      } finally {
        setLoading(false);
      }
    };
    fetchRaids();
  }, []);

  // Add this function to reload raids from the API
  const reloadRaids = async () => {
    const updatedRaids = await RaidService.getRaids();
    setRaids(updatedRaids);
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

  // Placeholder for add/edit/delete handlers
  const handleAddRaid = async (values: { warcraftlogs_url: string; team_id: number; scenario_id: number; scheduled_at: string }) => {
    setFormLoading(true);
    setFormError(null);
    try {
      await RaidService.createRaid({
        scheduled_at: values.scheduled_at,
        team_id: values.team_id,
        scenario_id: values.scenario_id,
        // warcraftlogs_url is not part of RaidCreate, so do not send it here
      });
      setShowAddForm(false);
      await reloadRaids();
    } catch (err: any) {
      setFormError(err.message || 'Failed to add raid');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditRaid = async (values: { warcraftlogs_url: string; team_id: number; scenario_id: number; scheduled_at: string }) => {
    if (!editingRaid) return;
    setFormLoading(true);
    setFormError(null);
    try {
      await RaidService.updateRaid(editingRaid.id, {
        scheduled_at: values.scheduled_at,
        team_id: values.team_id,
        scenario_id: values.scenario_id,
        // warcraftlogs_url is not part of RaidUpdate, so do not send it here
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
    if (!confirm('Are you sure you want to delete this raid?')) return;
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

  // Filter raids based on search (by ID for now)
  const filteredRaids = raids.filter(raid => {
    return raid.id.toString().includes(searchTerm);
  });

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
          {/* Search Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  placeholder="Search by raid ID..."
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

          {/* Raids List */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Raids</h2>
              <div className="text-sm text-slate-400">
                {filteredRaids.length} of {raids.length} raids
              </div>
            </div>

            {filteredRaids.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-slate-400 text-6xl mb-4">🗡️</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {searchTerm ? 'No raids found' : 'No raids yet'}
                </h3>
                <p className="text-slate-400 mb-6">
                  {searchTerm 
                    ? 'Try adjusting your search terms' 
                    : 'Get started by adding your first raid'
                  }
                </p>
                {!searchTerm && (
                  <Button variant="primary" onClick={openAddForm}>
                    Add First Raid
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredRaids.map(raid => (
                  <div
                    key={raid.id}
                    className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:border-slate-600/50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <span className="text-white font-medium">Raid #{raid.id}</span>
                      <div className="flex items-center space-x-4 text-sm text-slate-400">
                        <span>{raid.scheduled_at}</span>
                        <span>•</span>
                        <span>Team ID: {raid.team_id}</span>
                        <span>•</span>
                        <span>Scenario ID: {raid.scenario_id}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md">
            <RaidForm
              teams={teams}
              scenarios={scenarios}
              loading={formLoading}
              error={formError}
              onSubmit={showAddForm ? handleAddRaid : handleEditRaid}
              onCancel={handleCancelForm}
              initialValues={editingRaid ? {
                scheduled_at: editingRaid.scheduled_at,
                team_id: editingRaid.team_id,
                scenario_id: editingRaid.scenario_id,
              } : {}}
            />
          </div>
        </div>
      )}
    </div>
  );
} 