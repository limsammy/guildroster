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

const WOW_ROLES = ['Melee DPS', 'Ranged DPS', 'Healer', 'Tank'];

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
    <Card variant="elevated" className="max-w-md mx-auto p-3 sm:p-6">
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
          <label className="block text-sm font-medium text-slate-300 mb-2">Teams</label>
          <div className="flex flex-col gap-2">
            {teams.map(team => {
              const selected = selectedTeamIds.includes(team.id);
              return (
                <button
                  key={team.id}
                  type="button"
                  className="flex items-center gap-2 group"
                  onClick={() => {
                    setSelectedTeamIds(selected
                      ? selectedTeamIds.filter(id => id !== team.id)
                      : [...selectedTeamIds, team.id]
                    );
                  }}
                >
                  <span
                    className={`w-7 h-7 rounded-full flex items-center justify-center border-2 transition
                      ${selected ? 'bg-amber-500 border-amber-500 text-white' : 'bg-slate-800 border-slate-600 text-slate-300'}
                      group-focus:ring-2 group-focus:ring-amber-500`}
                    style={{ fontSize: '0.9rem' }}
                  >
                    {selected ? '✓' : ''}
                  </span>
                  <span className="text-xs text-slate-200">{team.name}</span>
                </button>
              );
            })}
          </div>
        </div>
        <div className="flex flex-col sm:flex-row justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading} className="w-full sm:w-auto">
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !username.trim() || !class_ || !role} 
            data-testid="toon-form-submit"
            className="w-full sm:w-auto"
          >
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Toon' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 