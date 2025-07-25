import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router';
import { Button, Card, Container } from '../components/ui';
import { ToonForm } from '../components/ui/ToonForm';
import { TeamService } from '../api/teams';
import { ToonService } from '../api/toons';
import type { Team, Toon, ToonCreate, ToonUpdate } from '../api/types';
import { getClassColor } from '../utils/classColors';

export default function TeamView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [team, setTeam] = useState<Team | null>(null);
  const [toons, setToons] = useState<Toon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showToonForm, setShowToonForm] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [allTeams, setAllTeams] = useState<Team[]>([]);
  const [editingToon, setEditingToon] = useState<Toon | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const teamData = await TeamService.getTeam(Number(id));
        setTeam(teamData);
        const allToons = await ToonService.getToons();
        setToons(allToons.filter(t => t.team_ids.includes(Number(id))));
        // Fetch all teams for the selector
        const teamsData = await TeamService.getTeams();
        setAllTeams(teamsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load team');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleAddToon = async (values: ToonCreate) => {
    setFormLoading(true);
    setFormError(null);
    try {
      // Auto-assign to this team
      await ToonService.createToon({ ...values, team_ids: [Number(id)] });
      // Refresh toon list
      const allToons = await ToonService.getToons();
      setToons(allToons.filter(t => t.team_ids.includes(Number(id))));
      setShowToonForm(false);
    } catch (err: any) {
      setFormError(err.message || 'Failed to create character');
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateToon = async (values: ToonUpdate) => {
    if (!editingToon) return;
    setFormLoading(true);
    setFormError(null);
    try {
      await ToonService.updateToon(editingToon.id, values);
      const allToons = await ToonService.getToons();
      setToons(allToons.filter(t => t.team_ids.includes(Number(id))));
      setEditingToon(null);
    } catch (err: any) {
      setFormError(err.message || 'Failed to update character');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteToon = async (toonId: number) => {
    if (!confirm('Are you sure you want to delete this character?')) return;
    setDeleteLoading(true);
    try {
      await ToonService.deleteToon(toonId);
      const allToons = await ToonService.getToons();
      setToons(allToons.filter(t => t.team_ids.includes(Number(id))));
    } catch (err: any) {
      alert('Failed to delete character');
    } finally {
      setDeleteLoading(false);
    }
  };

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case 'Tank':
        return 'bg-blue-600 text-white';
      case 'Healer':
        return 'bg-green-500 text-white';
      case 'Melee DPS':
        return 'bg-red-500 text-white';
      case 'Ranged DPS':
        return 'bg-purple-500 text-white';
      default:
        return 'bg-amber-500 text-white';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading team...</p>
        </div>
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Team</h2>
          <p className="text-slate-300 mb-4">{error || 'Team not found'}</p>
          <Button onClick={() => navigate(-1)}>Back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Container>
        <div className="py-4">
          {/* Compact Header */}
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-white">{team.name}</h1>
              <p className="text-slate-400 text-sm">Team ID: {team.id}</p>
              {typeof (team as any).description === 'string' && (team as any).description && (
                <p className="text-slate-300 text-sm mt-1">{(team as any).description}</p>
              )}
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" onClick={() => navigate(-1)}>Back</Button>
              <Button size="sm" variant="primary" onClick={() => setShowToonForm(true)}>Add Character</Button>
            </div>
          </div>

          {/* Compact Character List */}
          <Card variant="elevated" className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-bold text-white">Characters ({toons.length})</h2>
            </div>
            {toons.length === 0 ? (
              <div className="text-slate-400 text-center py-6">No characters assigned to this team yet.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                {toons.map(toon => (
                  <div key={toon.id} className="bg-slate-800 rounded-lg border border-slate-700/50 p-3 hover:bg-slate-750 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <div className={`text-base font-bold truncate ${getClassColor(toon.class)}`} title={toon.username}>
                          {toon.username}
                        </div>
                        <div className="text-slate-300 text-xs">Class: {toon.class}</div>
                      </div>
                      <div className="flex items-center gap-1 ml-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getRoleBadgeClass(toon.role)}`}>
                          {toon.role}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button 
                        size="sm" 
                        variant="secondary" 
                        onClick={() => setEditingToon(toon)}
                        className="text-xs px-2 py-1"
                      >
                        Edit
                      </Button>
                      <Button 
                        size="sm" 
                        variant="danger" 
                        onClick={() => handleDeleteToon(toon.id)} 
                        disabled={deleteLoading}
                        className="text-xs px-2 py-1"
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Add Character Modal */}
          {showToonForm && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="w-full max-w-md">
                <ToonForm
                  mode="add"
                  teams={allTeams}
                  initialValues={{ team_ids: [team.id] }}
                  loading={formLoading}
                  error={formError}
                  onSubmit={handleAddToon}
                  onCancel={() => setShowToonForm(false)}
                />
              </div>
            </div>
          )}

          {/* Edit Character Modal */}
          {editingToon && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="w-full max-w-md">
                <ToonForm
                  mode="edit"
                  teams={allTeams}
                  initialValues={editingToon}
                  loading={formLoading}
                  error={formError}
                  onSubmit={handleUpdateToon}
                  onCancel={() => setEditingToon(null)}
                />
              </div>
            </div>
          )}
        </div>
      </Container>
    </div>
  );
} 