import React, { useState, useEffect } from 'react';
import { TeamService } from '../../api/teams';
import type { Team } from '../../api/types';

interface TeamDropdownProps {
  selectedTeamId: number | null;
  onTeamChange: (teamId: number | null) => void;
  guildId?: number | null;
  className?: string;
}

export function TeamDropdown({ selectedTeamId, onTeamChange, guildId, className = '' }: TeamDropdownProps) {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        setLoading(true);
        setError(null);
        let teamsData: Team[];
        
        if (guildId) {
          // Get teams for specific guild
          teamsData = await TeamService.getTeamsByGuild(guildId);
        } else {
          // Get all teams
          teamsData = await TeamService.getTeams();
        }
        
        setTeams(teamsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load teams');
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, [guildId]);

  if (loading) {
    return (
      <select 
        className={`w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-slate-400 ${className}`}
        disabled
      >
        <option>Loading teams...</option>
      </select>
    );
  }

  if (error) {
    return (
      <select 
        className={`w-full px-3 py-2 bg-slate-800 border border-red-600 rounded-lg text-red-400 ${className}`}
        disabled
      >
        <option>Error loading teams</option>
      </select>
    );
  }

  return (
    <select
      value={selectedTeamId || ''}
      onChange={(e) => onTeamChange(e.target.value ? Number(e.target.value) : null)}
      className={`w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent ${className}`}
    >
      <option value="">Select Team</option>
      {teams.map(team => (
        <option key={team.id} value={team.id}>
          {team.name}
        </option>
      ))}
    </select>
  );
} 