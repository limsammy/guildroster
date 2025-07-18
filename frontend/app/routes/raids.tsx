import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { RaidService } from '../api/raids';
import type { Raid } from '../api/types';

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

  // Placeholder for add/edit/delete handlers
  const handleAddRaid = async (values: any) => {
    // TODO: Implement RaidForm and actual logic
    setShowAddForm(false);
  };

  const handleEditRaid = async (values: any) => {
    // TODO: Implement RaidForm and actual logic
    setEditingRaid(null);
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
                <Button variant="primary" onClick={() => setShowAddForm(true)}>
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
                  <Button variant="primary" onClick={() => setShowAddForm(true)}>
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
                        onClick={() => setEditingRaid(raid)}
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

      {/* Add/Edit Form Modal (placeholder) */}
      {(showAddForm || editingRaid) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md">
            <Card variant="elevated" className="p-6 text-center">
              <div className="mb-4">
                <span className="text-lg text-slate-300">Raid form coming soon...</span>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="secondary" onClick={handleCancelForm}>Cancel</Button>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
} 