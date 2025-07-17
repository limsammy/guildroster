import React, { useState, useEffect } from 'react';
import { Button, Card } from './';
import { MemberService, TeamService } from '../../api';
import type { Member, Team } from '../../api/types';

interface MemberSelectorProps {
  onMemberSelect: (member: Member) => void;
  onCancel: () => void;
}

export const MemberSelector: React.FC<MemberSelectorProps> = ({
  onMemberSelect,
  onCancel,
}) => {
  const [members, setMembers] = useState<Member[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [teamFilter, setTeamFilter] = useState<number | ''>('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [membersData, teamsData] = await Promise.all([
        MemberService.getMembers(),
        TeamService.getTeams(),
      ]);

      setMembers(membersData);
      setTeams(teamsData);
    } catch (err: any) {
      console.error('Error loading data:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const filteredMembers = members.filter(member => {
    const matchesSearch = member.display_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTeam = teamFilter === '' || member.team_id === teamFilter;
    return matchesSearch && matchesTeam;
  });

  const getTeamName = (teamId?: number) => {
    if (!teamId) return 'No Team';
    return teams.find(t => t.id === teamId)?.name || 'Unknown Team';
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
          <Button onClick={onCancel}>Go Back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="bg-slate-800/60 border-b border-slate-600/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                  Select Member
                </h1>
                <p className="text-slate-300 mt-1">
                  Choose a member to create a character for
                </p>
              </div>
              <Button variant="secondary" onClick={onCancel}>
                Cancel
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-8">
          {/* Search and Filter Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Search Members
                </label>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search by member name..."
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Filter by Team
                </label>
                <select
                  value={teamFilter}
                  onChange={(e) => setTeamFilter(e.target.value ? Number(e.target.value) : '')}
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
                    setTeamFilter('');
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </Card>

          {/* Results Count */}
          <div className="mb-4">
            <p className="text-slate-400">
              {filteredMembers.length} member{filteredMembers.length !== 1 ? 's' : ''} found
            </p>
          </div>

          {/* Members Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMembers.map((member) => (
              <Card key={member.id} variant="elevated" className="p-6 hover:bg-slate-800/50 transition-colors">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">{member.display_name}</h3>
                    <p className="text-slate-300 text-sm">{getTeamName(member.team_id)}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={() => onMemberSelect(member)}
                  >
                    Select
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          {filteredMembers.length === 0 && (
            <Card variant="elevated" className="p-12 text-center">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-xl font-semibold text-white mb-2">
                {members.length === 0 ? 'No Members Found' : 'No Members Match Search'}
              </h3>
              <p className="text-slate-300 mb-6">
                {members.length === 0 
                  ? 'Create some members first before adding characters'
                  : 'Try adjusting your search criteria'
                }
              </p>
              {members.length === 0 && (
                <Button onClick={onCancel}>
                  Go Back
                </Button>
              )}
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}; 