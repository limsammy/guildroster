import React, { useState } from 'react';
import { Button, Card } from './';
import type { Guild } from '../../api/types';

interface GuildFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Guild>;
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { name: string }) => void;
  onCancel: () => void;
}

export const GuildForm: React.FC<GuildFormProps> = ({
  mode,
  initialValues = {},
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState(initialValues.name || '');
  const [showErrors, setShowErrors] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!name.trim()) return;
    onSubmit({
      name: name.trim(),
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const nameError = showErrors && !name.trim() ? 'Name is required' : '';

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">
          {mode === 'add' ? 'Add Guild' : 'Edit Guild'}
        </h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        <div className="mb-6">
          <label htmlFor="guild-name" className="block text-sm font-medium text-slate-300 mb-2">
            Guild Name
          </label>
          <input
            id="guild-name"
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyPress={handleKeyPress}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="Enter guild name"
            disabled={loading}
          />
          {nameError && <div className="text-red-400 text-xs mt-1">{nameError}</div>}
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !name.trim()} 
            data-testid="guild-form-submit"
          >
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Guild' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 