import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container } from "../components/ui";
import { MemberForm } from "../components/ui/MemberForm";
import { useAuth } from "../contexts/AuthContext";
import { MemberService } from "../api/members";
import { GuildService } from "../api/guilds";
import { TeamService } from "../api/teams";
import { ToonService } from "../api/toons";
import type { Member, Guild, Team, Toon } from "../api/types";

export function meta() {
  return [
    { title: "Members - GuildRoster" },
    { name: "description", content: "Manage guild members, their team assignments, and character rosters." },
  ];
}

export default function Members() {
  const { user } = useAuth();
  const [members, setMembers] = useState<Member[]>([]);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [toons, setToons] = useState<Toon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGuild, setSelectedGuild] = useState<number | ''>('');
  const [selectedTeam, setSelectedTeam] = useState<number | ''>('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [membersData, guildsData, teamsData, toonsData] = await Promise.all([
          MemberService.getMembers(),
          GuildService.getGuilds(),
          TeamService.getTeams(),
          ToonService.getToons(),
        ]);

        setMembers(membersData);
        setGuilds(guildsData);
        setTeams(teamsData);
        setToons(toonsData);
      } catch (err: any) {
        console.error('Error fetching members data:', err);
        setError(err.message || 'Failed to load members data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Add this function to reload members from the API
  const reloadMembers = async () => {
    const updatedMembers = await MemberService.getMembers();
    setMembers(updatedMembers);
  };

  const handleAddMember = async (values: { display_name: string; guild_id: number; team_id?: number | null }) => {
    try {
      setFormLoading(true);
      setFormError(null);
      const memberData = {
        display_name: values.display_name,
        guild_id: values.guild_id,
        team_id: values.team_id ? values.team_id : undefined,
      };
      await MemberService.createMember(memberData);
      await reloadMembers();
      setShowAddForm(false);
    } catch (err: any) {
      console.error('Error creating member:', err);
      const msg = err.message || '';
      setFormError(msg.toLowerCase().includes('create failed') ? 'Create failed' : msg || 'Failed to create member');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditMember = async (values: { display_name: string; guild_id: number; team_id?: number | null }) => {
    if (!editingMember) return;
    try {
      setFormLoading(true);
      setFormError(null);
      const memberData = {
        display_name: values.display_name,
        guild_id: values.guild_id,
        team_id: values.team_id ? values.team_id : undefined,
      };
      await MemberService.updateMember(editingMember.id, memberData);
      await reloadMembers();
      setEditingMember(null);
    } catch (err: any) {
      console.error('Error updating member:', err);
      setFormError(err.message || 'Failed to update member');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteMember = async (memberId: number) => {
    if (!confirm('Are you sure you want to delete this member?')) return;
    
    try {
      await MemberService.deleteMember(memberId);
      await reloadMembers();
    } catch (err: any) {
      console.error('Error deleting member:', err);
      alert('Failed to delete member: ' + (err.message || 'Unknown error'));
    }
  };

  const handleCancelForm = () => {
    setShowAddForm(false);
    setEditingMember(null);
    setFormError(null);
  };

  // Filter members based on search and filters
  const filteredMembers = members.filter(member => {
    const matchesSearch = member.display_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesGuild = selectedGuild === '' || member.guild_id === selectedGuild;
    const matchesTeam = selectedTeam === '' || member.team_id === selectedTeam;
    
    return matchesSearch && matchesGuild && matchesTeam;
  });

  // Get member's toons count
  const getMemberToonsCount = (memberId: number) => {
    return toons.filter(toon => toon.member_id === memberId).length;
  };

  // Get guild name
  const getGuildName = (guildId: number) => {
    return guilds.find(g => g.id === guildId)?.name || 'Unknown Guild';
  };

  // Get team name
  const getTeamName = (teamId?: number) => {
    if (!teamId) return 'No Team';
    return teams.find(t => t.id === teamId)?.name || 'Unknown Team';
  };

  // Get teams for a specific guild
  const getTeamsForGuild = (guildId: number) => {
    return teams.filter(team => team.guild_id === guildId);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading members...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Members</h2>
          <p className="text-slate-300 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
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
                  <span className="text-slate-300">Members</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                  Guild Members
                </h1>
                <p className="text-slate-300 mt-1">
                  Manage your guild's member roster and team assignments
                </p>
              </div>
              <div className="flex gap-3">
                <Link to="/dashboard">
                  <Button variant="secondary">Back to Dashboard</Button>
                </Link>
                <Button onClick={() => setShowAddForm(true)}>
                  Add Member
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Filters and Search */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Search Members
                </label>
                <input
                  type="text"
                  placeholder="Search by name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Filter by Guild
                </label>
                <select
                  value={selectedGuild}
                  onChange={(e) => setSelectedGuild(e.target.value ? Number(e.target.value) : '')}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  <option value="">All Guilds</option>
                  {guilds.map(guild => (
                    <option key={guild.id} value={guild.id}>{guild.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Filter by Team
                </label>
                <select
                  value={selectedTeam}
                  onChange={(e) => setSelectedTeam(e.target.value ? Number(e.target.value) : '')}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  <option value="">All Teams</option>
                  {teams.map(team => (
                    <option key={team.id} value={team.id}>{team.name}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <Button 
                  variant="secondary" 
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedGuild('');
                    setSelectedTeam('');
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </Card>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-amber-400 mb-2">{members.length}</div>
              <div className="text-slate-300">Total Members</div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-blue-400 mb-2">
                {members.filter(m => m.team_id).length}
              </div>
              <div className="text-slate-300">Assigned to Teams</div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-green-400 mb-2">
                {members.filter(m => !m.team_id).length}
              </div>
              <div className="text-slate-300">Unassigned</div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-purple-400 mb-2">{toons.length}</div>
              <div className="text-slate-300">Total Characters</div>
            </Card>
          </div>

          {/* Members Table */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">
                Members ({filteredMembers.length})
              </h2>
              <div className="flex gap-2">
                <Button size="sm" variant="secondary">
                  Export
                </Button>
                <Button size="sm" variant="secondary">
                  Bulk Actions
                </Button>
              </div>
            </div>

            {filteredMembers.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">👥</div>
                <h3 className="text-xl font-semibold text-white mb-2">No Members Found</h3>
                <p className="text-slate-300 mb-4">
                  {searchTerm || selectedGuild || selectedTeam 
                    ? 'Try adjusting your search or filters'
                    : 'Get started by adding your first guild member'
                  }
                </p>
                {!searchTerm && !selectedGuild && !selectedTeam && (
                  <Button onClick={() => setShowAddForm(true)}>
                    Add First Member
                  </Button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-600/50">
                      <th className="text-left py-3 px-4 text-slate-300 font-medium">Name</th>
                      <th className="text-left py-3 px-4 text-slate-300 font-medium">Guild</th>
                      <th className="text-left py-3 px-4 text-slate-300 font-medium">Team</th>
                      <th className="text-left py-3 px-4 text-slate-300 font-medium">Characters</th>
                      <th className="text-left py-3 px-4 text-slate-300 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredMembers.map((member) => (
                      <tr key={member.id} className="border-b border-slate-600/30 hover:bg-slate-800/30">
                        <td className="py-4 px-4">
                          <div className="font-medium text-white">{member.display_name}</div>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-slate-300">{getGuildName(member.guild_id)}</span>
                        </td>
                        <td className="py-4 px-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            member.team_id 
                              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                              : 'bg-slate-500/20 text-slate-300 border border-slate-500/30'
                          }`}>
                            {getTeamName(member.team_id)}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-slate-300">
                            {getMemberToonsCount(member.id)} character{getMemberToonsCount(member.id) !== 1 ? 's' : ''}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex gap-2">
                            <Link to={`/members/${member.id}`}>
                              <Button size="sm" variant="ghost">
                                View
                              </Button>
                            </Link>
                            <Button 
                              size="sm" 
                              variant="ghost"
                              onClick={() => setEditingMember(member)}
                            >
                              Edit
                            </Button>
                            <Button 
                              size="sm" 
                              variant="danger"
                              onClick={() => handleDeleteMember(member.id)}
                            >
                              Delete
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      </Container>

      {/* Member Form Modal */}
      {(showAddForm || editingMember) && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" data-testid="member-form-modal">
          <div className="w-full max-w-md">
            <MemberForm
              mode={showAddForm ? 'add' : 'edit'}
              initialValues={editingMember || undefined}
              guilds={guilds}
              teams={teams}
              loading={formLoading}
              error={formError}
              onSubmit={showAddForm ? handleAddMember : handleEditMember}
              onCancel={handleCancelForm}
            />
          </div>
        </div>
      )}
    </div>
  );
} 