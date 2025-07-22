import React, { useState } from 'react';
import { Button, Card } from './';
import type { Scenario } from '../../api/types';

interface ScenarioFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Scenario>;
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { name: string; is_active: boolean; mop: boolean }) => void;
  onCancel: () => void;
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({
  mode,
  initialValues = {},
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState(initialValues.name || '');
  const [isActive, setIsActive] = useState(initialValues.is_active ?? true);
  const [mop, setMop] = useState(initialValues.mop ?? false);
  const [showErrors, setShowErrors] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!name.trim()) return;
    onSubmit({
      name: name.trim(),
      is_active: isActive,
      mop: mop,
    });
  };

  const nameError = showErrors && !name.trim() ? 'Name is required' : '';

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">
          {mode === 'add' ? 'Add Scenario Template' : 'Edit Scenario Template'}
        </h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="scenario-name" className="block text-sm font-medium text-slate-300 mb-2">
            Scenario Name
          </label>
          <input
            id="scenario-name"
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="Enter scenario name (e.g., Molten Core, Mogu'shan Vaults)"
            disabled={loading}
          />
          {nameError && <div className="text-red-400 text-xs mt-1">{nameError}</div>}
        </div>
        
        <div className="mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={mop}
              onChange={e => setMop(e.target.checked)}
              className="w-4 h-4 text-amber-500 bg-slate-800 border-slate-600 rounded focus:ring-amber-500 focus:ring-2"
              disabled={loading}
            />
            <span className="ml-2 text-sm text-slate-300">Mists of Pandaria Scenario</span>
          </label>
          <p className="text-xs text-slate-400 mt-1 ml-6">
            {mop 
              ? "✓ Will generate 8 variations (Normal, Heroic, Celestial, Challenge × 10/25-man)"
              : "✓ Will generate 4 variations (Normal, Heroic × 10/25-man)"
            }
          </p>
        </div>

        <div className="mb-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={isActive}
              onChange={e => setIsActive(e.target.checked)}
              className="w-4 h-4 text-amber-500 bg-slate-800 border-slate-600 rounded focus:ring-amber-500 focus:ring-2"
              disabled={loading}
            />
            <span className="ml-2 text-sm text-slate-300">Active</span>
          </label>
          <p className="text-xs text-slate-400 mt-1 ml-6">
            Active scenario templates are available for creating raids
          </p>
        </div>

        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 mb-6">
          <h4 className="text-blue-400 font-medium mb-2">Scenario Templating System</h4>
          <p className="text-blue-300 text-sm">
            This creates a scenario template that automatically generates all variations based on the MoP setting. 
            You only need to create one template per scenario - all difficulty and size combinations will be available automatically.
          </p>
        </div>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !name.trim()} 
            data-testid="scenario-form-submit"
          >
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Scenario Template' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 