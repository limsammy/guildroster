import React, { useState, useMemo } from 'react';
import { Button, Card } from './';
import type { Member, Guild, Team } from '../../api/types';

interface MemberFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Member>;
  guilds: Guild[];
  teams: Team[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { display_name: string; guild_id: number; team_id?: number | null }) => void;
  onCancel: () => void;
}

export const MemberForm: React.FC<MemberFormProps> = ({
  mode,
  initialValues = {},
  guilds,
  teams,
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [displayName, setDisplayName] = useState(initialValues.display_name || '');
  const [guildId, setGuildId] = useState<number | ''>(initialValues.guild_id ?? '');
  const [teamId, setTeamId] = useState<number | ''>(initialValues.team_id ?? '');
  const [showErrors, setShowErrors] = useState(false);

  const filteredTeams = useMemo(() => {
    if (!guildId) return [];
    return teams.filter(team => team.guild_id === guildId);
  }, [guildId, teams]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!displayName.trim() || !guildId) return;
    onSubmit({
      display_name: displayName.trim(),
      guild_id: Number(guildId),
      team_id: teamId ? Number(teamId) : null,
    });
  };

  const displayNameError = showErrors && !displayName.trim() ? 'Name is required' : '';
  const guildError = showErrors && !guildId ? 'Guild is required' : '';

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">
          {mode === 'add' ? 'Add Member' : 'Edit Member'}
        </h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="member-name" className="block text-sm font-medium text-slate-300 mb-2">Name</label>
          <input
            id="member-name"
            type="text"
            value={displayName}
            onChange={e => setDisplayName(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="Enter member name"
            disabled={loading}
          />
          {displayNameError && <div className="text-red-400 text-xs mt-1">{displayNameError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="member-guild" className="block text-sm font-medium text-slate-300 mb-2">Guild</label>
          <select
            id="member-guild"
            value={guildId}
            onChange={e => { setGuildId(e.target.value ? Number(e.target.value) : ''); setTeamId(''); }}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select a guild</option>
            {guilds.map(guild => (
              <option key={guild.id} value={guild.id}>{guild.name}</option>
            ))}
          </select>
          {guildError && <div className="text-red-400 text-xs mt-1">{guildError}</div>}
        </div>
        <div className="mb-6">
          <label htmlFor="member-team" className="block text-sm font-medium text-slate-300 mb-2">Team</label>
          <select
            id="member-team"
            value={teamId}
            onChange={e => setTeamId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading || !guildId}
          >
            <option value="">No Team</option>
            {filteredTeams.map(team => (
              <option key={team.id} value={team.id}>{team.name}</option>
            ))}
          </select>
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading || !displayName.trim() || guildId === ''} data-testid="member-form-submit">
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Member' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 