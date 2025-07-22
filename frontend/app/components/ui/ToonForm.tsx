import React, { useState } from 'react';
import { Button, Card } from './';
import type { Toon, Team } from '../../api/types';

interface ToonFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Toon>;
  teams: Team[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { username: string; class: string; role: string; team_ids?: number[] }) => void;
  onCancel: () => void;
}

// WoW classes and roles from backend
const WOW_CLASSES = [
  'Death Knight',
  'Warrior',
  'Druid',
  'Paladin',
  'Monk',
  'Rogue',
  'Hunter',
  'Mage',
  'Warlock',
  'Priest',
  'Shaman',
];

const WOW_ROLES = ['DPS', 'Healer', 'Tank'];

export const ToonForm: React.FC<ToonFormProps> = ({
  mode,
  initialValues = {},
  teams,
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [username, setUsername] = useState(initialValues.username || '');
  const [class_, setClass] = useState(initialValues.class || '');
  const [role, setRole] = useState(initialValues.role || '');
  const [selectedTeamIds, setSelectedTeamIds] = useState<number[]>(initialValues.team_ids || []);
  const [showErrors, setShowErrors] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!username.trim() || !class_ || !role) return;
    onSubmit({
      username: username.trim(),
      class: class_,
      role,
      team_ids: selectedTeamIds.length > 0 ? selectedTeamIds : undefined,
    });
  };

  const usernameError = showErrors && !username.trim() ? 'Username is required' : '';
  const classError = showErrors && !class_ ? 'Class is required' : '';
  const roleError = showErrors && !role ? 'Role is required' : '';

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">
          {mode === 'add' ? 'Add Toon' : 'Edit Toon'}
        </h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="toon-username" className="block text-sm font-medium text-slate-300 mb-2">Username</label>
          <input
            id="toon-username"
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="Enter character name"
            disabled={loading}
          />
          {usernameError && <div className="text-red-400 text-xs mt-1">{usernameError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="toon-class" className="block text-sm font-medium text-slate-300 mb-2">Class</label>
          <select
            id="toon-class"
            value={class_}
            onChange={e => setClass(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select class</option>
            {WOW_CLASSES.map(wowClass => (
              <option key={wowClass} value={wowClass}>{wowClass}</option>
            ))}
          </select>
          {classError && <div className="text-red-400 text-xs mt-1">{classError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="toon-role" className="block text-sm font-medium text-slate-300 mb-2">Role</label>
          <select
            id="toon-role"
            value={role}
            onChange={e => setRole(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select role</option>
            {WOW_ROLES.map(wowRole => (
              <option key={wowRole} value={wowRole}>{wowRole}</option>
            ))}
          </select>
          {roleError && <div className="text-red-400 text-xs mt-1">{roleError}</div>}
        </div>
        <div className="mb-6">
          <label htmlFor="toon-teams" className="block text-sm font-medium text-slate-300 mb-2">Teams</label>
          <select
            id="toon-teams"
            multiple
            value={selectedTeamIds.map(String)}
            onChange={e => {
              const options = Array.from(e.target.selectedOptions).map(opt => Number(opt.value));
              setSelectedTeamIds(options);
            }}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            {teams.map(team => (
              <option key={team.id} value={team.id}>{team.name}</option>
            ))}
          </select>
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !username.trim() || !class_ || !role} 
            data-testid="toon-form-submit"
          >
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Toon' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 