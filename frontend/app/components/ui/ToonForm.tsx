import React, { useState } from 'react';
import { Button, Card } from './';
import type { Toon, Member } from '../../api/types';

interface ToonFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Toon>;
  members: Member[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { username: string; class: string; role: string; is_main: boolean; member_id: number }) => void;
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
  members,
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [username, setUsername] = useState(initialValues.username || '');
  const [class_, setClass] = useState(initialValues.class || '');
  const [role, setRole] = useState(initialValues.role || '');
  const [isMain, setIsMain] = useState(initialValues.is_main ?? false);
  const [memberId, setMemberId] = useState<number | ''>(initialValues.member_id ?? '');
  const [showErrors, setShowErrors] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!username.trim() || !class_ || !role || !memberId) return;
    onSubmit({
      username: username.trim(),
      class: class_,
      role,
      is_main: isMain,
      member_id: Number(memberId),
    });
  };

  const usernameError = showErrors && !username.trim() ? 'Username is required' : '';
  const classError = showErrors && !class_ ? 'Class is required' : '';
  const roleError = showErrors && !role ? 'Role is required' : '';
  const memberError = showErrors && !memberId ? 'Member is required' : '';

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
          <label htmlFor="toon-username" className="block text-sm font-medium text-slate-300 mb-2">
            Username
          </label>
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
          <label htmlFor="toon-class" className="block text-sm font-medium text-slate-300 mb-2">
            Class
          </label>
          <select
            id="toon-class"
            value={class_}
            onChange={e => setClass(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select a class</option>
            {WOW_CLASSES.map(wowClass => (
              <option key={wowClass} value={wowClass}>{wowClass}</option>
            ))}
          </select>
          {classError && <div className="text-red-400 text-xs mt-1">{classError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="toon-role" className="block text-sm font-medium text-slate-300 mb-2">
            Role
          </label>
          <select
            id="toon-role"
            value={role}
            onChange={e => setRole(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select a role</option>
            {WOW_ROLES.map(wowRole => (
              <option key={wowRole} value={wowRole}>{wowRole}</option>
            ))}
          </select>
          {roleError && <div className="text-red-400 text-xs mt-1">{roleError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="toon-member" className="block text-sm font-medium text-slate-300 mb-2">
            Member
          </label>
          <select
            id="toon-member"
            value={memberId}
            onChange={e => setMemberId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select a member</option>
            {members.map(member => (
              <option key={member.id} value={member.id}>{member.name}</option>
            ))}
          </select>
          {memberError && <div className="text-red-400 text-xs mt-1">{memberError}</div>}
        </div>
        <div className="mb-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={isMain}
              onChange={e => setIsMain(e.target.checked)}
              className="w-4 h-4 text-amber-500 bg-slate-800 border-slate-600 rounded focus:ring-amber-500 focus:ring-2"
              disabled={loading}
            />
            <span className="ml-2 text-sm text-slate-300">Main character</span>
          </label>
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !username.trim() || !class_ || !role || memberId === ''} 
            data-testid="toon-form-submit"
          >
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Toon' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 