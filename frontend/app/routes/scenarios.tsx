import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container, ScenarioForm } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { ScenarioService } from '../api/scenarios';
import type { Scenario } from '../api/types';
import { exportJson } from '../utils/exportJson';

export function meta() {
  return [
    { title: 'Scenarios - GuildRoster' },
    { name: 'description', content: 'Manage scenarios and their settings.' },
  ];
}

export default function Scenarios() {
  const { user } = useAuth();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingScenario, setEditingScenario] = useState<Scenario | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        setLoading(true);
        setError(null);
        const scenariosData = await ScenarioService.getScenarios();
        setScenarios(scenariosData);
      } catch (err: any) {
        setError(err.message || 'Failed to load scenarios');
      } finally {
        setLoading(false);
      }
    };
    fetchScenarios();
  }, []);

  // Add this function to reload scenarios from the API
  const reloadScenarios = async () => {
    const updatedScenarios = await ScenarioService.getScenarios();
    setScenarios(updatedScenarios);
  };

  const handleAddScenario = async (values: { name: string; is_active: boolean; mop: boolean }) => {
    setFormLoading(true);
    setFormError(null);
    try {
      await ScenarioService.createScenario(values);
      setShowAddForm(false);
      await reloadScenarios();
    } catch (err: any) {
      setFormError(err.message || 'Failed to add scenario');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditScenario = async (values: { name: string; is_active: boolean; mop: boolean }) => {
    if (!editingScenario) return;
    setFormLoading(true);
    setFormError(null);
    try {
      await ScenarioService.updateScenario(editingScenario.id, values);
      setEditingScenario(null);
      await reloadScenarios();
    } catch (err: any) {
      setFormError(err.message || 'Failed to update scenario');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteScenario = async (scenarioId: number) => {
    if (!confirm('Are you sure you want to delete this scenario? This action cannot be undone.')) return;
    
    try {
      await ScenarioService.deleteScenario(scenarioId);
      await reloadScenarios();
    } catch (err: any) {
      console.error('Error deleting scenario:', err);
      alert('Failed to delete scenario: ' + (err.message || 'Unknown error'));
    }
  };

  const handleCancelForm = () => {
    setShowAddForm(false);
    setEditingScenario(null);
    setFormError(null);
  };

  // Filter scenarios based on search
  const filteredScenarios = scenarios.filter(scenario => {
    const matchesSearch = scenario.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Calculate statistics
  const totalScenarios = scenarios.length;
  const activeScenarios = scenarios.filter(s => s.is_active).length;
  const inactiveScenarios = scenarios.filter(s => !s.is_active).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading scenarios...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Scenarios</h2>
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
                  <span className="text-slate-300">Scenarios</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Scenarios</h1>
                <p className="text-slate-300 mt-1">Manage your scenarios and their settings</p>
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" onClick={() => exportJson(scenarios, 'scenarios.json')}>
                  Export as JSON
                </Button>
                <Link to="/dashboard">
                  <Button variant="secondary">Dashboard</Button>
                </Link>
                <Button variant="primary" onClick={() => setShowAddForm(true)}>
                  Add Scenario
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-amber-400 mb-2">{totalScenarios}</div>
              <div className="text-slate-300">Total Scenarios</div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-green-400 mb-2">{activeScenarios}</div>
              <div className="text-slate-300">Active Scenarios</div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-slate-400 mb-2">{inactiveScenarios}</div>
              <div className="text-slate-300">Inactive Scenarios</div>
            </Card>
          </div>

          {/* Search Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="search" className="block text-sm font-medium text-slate-300 mb-2">
                  Search Scenarios
                </label>
                <input
                  id="search"
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder="Search by scenario name..."
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

          {/* Scenarios List */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Scenarios</h2>
              <div className="text-sm text-slate-400">
                {filteredScenarios.length} of {scenarios.length} scenarios
              </div>
            </div>

            {filteredScenarios.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-slate-400 text-6xl mb-4">🎮</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {searchTerm ? 'No scenarios found' : 'No scenarios yet'}
                </h3>
                <p className="text-slate-400 mb-6">
                  {searchTerm 
                    ? 'Try adjusting your search terms' 
                    : 'Get started by adding your first scenario'
                  }
                </p>
                {!searchTerm && (
                  <Button variant="primary" onClick={() => setShowAddForm(true)}>
                    Add First Scenario
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredScenarios.map(scenario => (
                  <div
                    key={scenario.id}
                    className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:border-slate-600/50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${scenario.is_active ? 'bg-green-400' : 'bg-slate-500'}`}></div>
                        <span className="text-white font-medium">{scenario.name}</span>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-slate-400">
                        <span>{scenario.is_active ? 'Active' : 'Inactive'}</span>
                        <span>•</span>
                        <span>{scenario.mop ? 'MoP (4 difficulties)' : 'Non-MoP (2 difficulties)'}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setEditingScenario(scenario)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteScenario(scenario.id)}
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
      {(showAddForm || editingScenario) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md">
            <ScenarioForm
              mode={showAddForm ? 'add' : 'edit'}
              initialValues={editingScenario || {}}
              loading={formLoading}
              error={formError}
              onSubmit={showAddForm ? handleAddScenario : handleEditScenario}
              onCancel={handleCancelForm}
            />
          </div>
        </div>
      )}
    </div>
  );
} 