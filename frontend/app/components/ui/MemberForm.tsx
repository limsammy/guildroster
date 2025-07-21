import React, { useState, useMemo } from 'react';
import { Button, Card } from './';
import type { Member, Guild, Team } from '../../api/types';

interface MemberFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Member>;
  guilds: Guild[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { display_name: string; guild_id: number }) => void;
  onCancel: () => void;
}

export const MemberForm: React.FC<MemberFormProps> = ({
  mode,
  initialValues = {},
  guilds,
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [displayName, setDisplayName] = useState(initialValues.display_name || '');
  // Auto-select first guild if adding and none is set
  const initialGuildId = initialValues.guild_id ?? (mode === 'add' && guilds.length > 0 ? guilds[0].id : '');
  const [guildId, setGuildId] = useState<number | ''>(initialGuildId);
  const [showErrors, setShowErrors] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!displayName.trim() || !guildId) return;
    onSubmit({
      display_name: displayName.trim(),
      guild_id: Number(guildId),
    });
  };

  const displayNameError = showErrors && !displayName.trim() ? 'Name is required' : '';
  const guildError = showErrors && !guildId ? 'Guild is required' : '';

  // If no guilds exist, disable the form and show a message
  const noGuilds = guilds.length === 0;

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
        {noGuilds && (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 mb-4">
            <p className="text-yellow-400 text-sm">You must create a guild before adding members.</p>
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
            disabled={loading || noGuilds}
          />
          {displayNameError && <div className="text-red-400 text-xs mt-1">{displayNameError}</div>}
        </div>
        <div className="mb-6">
          <label htmlFor="member-guild" className="block text-sm font-medium text-slate-300 mb-2">Guild</label>
          <select
            id="member-guild"
            value={guildId}
            onChange={e => setGuildId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading || noGuilds}
          >
            <option value="">Select a guild</option>
            {guilds.map(guild => (
              <option key={guild.id} value={guild.id}>{guild.name}</option>
            ))}
          </select>
          {guildError && <div className="text-red-400 text-xs mt-1">{guildError}</div>}
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading || !displayName.trim() || guildId === '' || noGuilds} data-testid="member-form-submit">
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Member' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 