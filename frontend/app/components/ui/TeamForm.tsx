import React, { useState } from 'react';
import { Button, Card } from './';
import type { Team, Guild } from '../../api/types';

interface TeamFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Team>;
  guilds: Guild[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { name: string; guild_id: number }) => void;
  onCancel: () => void;
}

export const TeamForm: React.FC<TeamFormProps> = ({
  mode,
  initialValues = {},
  guilds,
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState(initialValues.name || '');
  const [guildId, setGuildId] = useState<number | ''>(initialValues.guild_id ?? '');
  const [showErrors, setShowErrors] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!name.trim() || !guildId) return;
    onSubmit({
      name: name.trim(),
      guild_id: Number(guildId),
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const nameError = showErrors && !name.trim() ? 'Name is required' : '';
  const guildError = showErrors && !guildId ? 'Guild is required' : '';

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">
          {mode === 'add' ? 'Add Team' : 'Edit Team'}
        </h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="team-name" className="block text-sm font-medium text-slate-300 mb-2">
            Team Name
          </label>
          <input
            id="team-name"
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyPress={handleKeyPress}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="Enter team name"
            disabled={loading}
          />
          {nameError && <div className="text-red-400 text-xs mt-1">{nameError}</div>}
        </div>
        <div className="mb-6">
          <label htmlFor="team-guild" className="block text-sm font-medium text-slate-300 mb-2">
            Guild
          </label>
          <select
            id="team-guild"
            value={guildId}
            onChange={e => setGuildId(e.target.value ? Number(e.target.value) : '')}
            onKeyPress={handleKeyPress}
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
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !name.trim() || guildId === ''} 
            data-testid="team-form-submit"
          >
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Team' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 