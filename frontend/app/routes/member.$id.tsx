import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router';
import { Container, Button, Card } from '../components/ui';
import { ToonForm } from '../components/ui/ToonForm';
import { MemberService, ToonService, GuildService, TeamService } from '../api';
import type { Member, Toon, Guild, Team } from '../api/types';

export function meta() {
  return [
    { title: "Member Details - GuildRoster" },
    { name: "description", content: "View member details and manage their characters." },
  ];
}

export default function MemberDetail() {
  const { id } = useParams();
  const memberId = parseInt(id!);
  
  const [member, setMember] = useState<Member | null>(null);
  const [toons, setToons] = useState<Toon[]>([]);
  const [guild, setGuild] = useState<Guild | null>(null);
  const [team, setTeam] = useState<Team | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showToonForm, setShowToonForm] = useState(false);
  const [editingToon, setEditingToon] = useState<Toon | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (memberId) {
      loadMemberData();
    }
  }, [memberId]);

  const loadMemberData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [memberData, toonsData, teamsData] = await Promise.all([
        MemberService.getMember(memberId),
        ToonService.getToonsByMember(memberId),
        TeamService.getTeams(),
      ]);

      setMember(memberData);
      setToons(toonsData);
      setTeams(teamsData);

      // Load guild and team data
      if (memberData.guild_id) {
        const guildData = await GuildService.getGuild(memberData.guild_id);
        setGuild(guildData);
      }

      if (memberData.team_id) {
        const teamData = await TeamService.getTeam(memberData.team_id);
        setTeam(teamData);
      }
    } catch (err: any) {
      console.error('Error loading member data:', err);
      setError(err.message || 'Failed to load member data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateToon = async (values: { username: string; class: string; role: string; is_main: boolean; member_id: number; team_ids?: number[] }) => {
    try {
      setFormLoading(true);
      setFormError(null);
      await ToonService.createToon(values);
      await loadMemberData(); // Reload toons
      setShowToonForm(false);
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to create toon');
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateToon = async (values: { username: string; class: string; role: string; is_main: boolean; member_id: number; team_ids?: number[] }) => {
    if (!editingToon) return;
    try {
      setFormLoading(true);
      setFormError(null);
      await ToonService.updateToon(editingToon.id, values);
      await loadMemberData(); // Reload toons
      setEditingToon(null);
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to update toon');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteToon = async (toonId: number) => {
    if (!confirm('Are you sure you want to delete this toon?')) return;
    try {
      await ToonService.deleteToon(toonId);
      await loadMemberData(); // Reload toons
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete toon');
    }
  };

  const handleEditToon = (toon: Toon) => {
    setEditingToon(toon);
  };

  const handleCancelToonForm = () => {
    setShowToonForm(false);
    setEditingToon(null);
    setFormError(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading member details...</p>
        </div>
      </div>
    );
  }

  if (error || !member) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Member</h2>
          <p className="text-slate-300 mb-4">{error || 'Member not found'}</p>
          <Link to="/members">
            <Button>Back to Members</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (showToonForm || editingToon) {
    return (
      <Container>
        <div className="py-8">
          <ToonForm
            mode={editingToon ? 'edit' : 'add'}
            initialValues={editingToon || { member_id: member.id }}
            members={[member]} // Only show this member
            teams={teams}
            loading={formLoading}
            error={formError}
            onSubmit={editingToon ? handleUpdateToon : handleCreateToon}
            onCancel={handleCancelToonForm}
            hideMemberSelect={!editingToon} // Hide member select when adding new toon
          />
        </div>
      </Container>
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
                  <Link to="/members" className="hover:text-amber-400">Members</Link>
                  <span>/</span>
                  <span className="text-slate-300">{member.display_name}</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                  {member.display_name}
                </h1>
                <p className="text-slate-300 mt-1">
                  Member Details & Character Management
                </p>
              </div>
              <div className="flex gap-3">
                <Link to="/members">
                  <Button variant="secondary">Back to Members</Button>
                </Link>
                <Button onClick={() => setShowToonForm(true)}>
                  Add Character
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Member Information */}
          <Card variant="elevated" className="p-6 mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">Member Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">Name</label>
                <p className="text-white font-medium">{member.display_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">Guild</label>
                <p className="text-white">{guild?.name || 'Unknown Guild'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">Team</label>
                <p className="text-white">{team?.name || 'No Team Assigned'}</p>
              </div>
            </div>
          </Card>

          {/* Characters Section */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Characters</h2>
              <div className="text-slate-400">
                {toons.length} character{toons.length !== 1 ? 's' : ''}
              </div>
            </div>

            {toons.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚔️</div>
                <h3 className="text-xl font-semibold text-white mb-2">No Characters Found</h3>
                <p className="text-slate-300 mb-6">
                  {member.display_name} doesn't have any characters yet. Add their first character to get started.
                </p>
                <Button onClick={() => setShowToonForm(true)}>
                  Add First Character
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {toons.map((toon) => (
                  <div key={toon.id} className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-white text-lg">{toon.username}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            toon.class === 'Death Knight' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                            toon.class === 'Warrior' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                            toon.class === 'Druid' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                            toon.class === 'Paladin' ? 'bg-pink-500/20 text-pink-300 border border-pink-500/30' :
                            toon.class === 'Monk' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                            toon.class === 'Rogue' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                            toon.class === 'Hunter' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                            toon.class === 'Mage' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                            toon.class === 'Warlock' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' :
                            toon.class === 'Priest' ? 'bg-white/20 text-white border border-white/30' :
                            toon.class === 'Shaman' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                            'bg-slate-500/20 text-slate-300 border border-slate-500/30'
                          }`}>
                            {toon.class}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            toon.role === 'Tank' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                            toon.role === 'Healer' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                            'bg-red-500/20 text-red-300 border border-red-500/30'
                          }`}>
                            {toon.role}
                          </span>
                          {toon.is_main && (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">
                              Main
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => handleEditToon(toon)}
                        >
                          Edit
                        </Button>
                        <Button 
                          size="sm" 
                          variant="danger"
                          onClick={() => handleDeleteToon(toon.id)}
                        >
                          Delete
                        </Button>
                      </div>
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