import React, { useState } from 'react';
import { Button, Card } from './';
import type { Scenario } from '../../api/types';

interface ScenarioFormProps {
  mode: 'add' | 'edit';
  initialValues?: Partial<Scenario>;
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { name: string; difficulty: string; size: string; is_active: boolean }) => void;
  onCancel: () => void;
}

// Difficulty and size options - must match backend SCENARIO_DIFFICULTIES and SCENARIO_SIZES
const DIFFICULTY_OPTIONS = ['Normal', 'Heroic', 'Celestial', 'Challenge'];
const SIZE_OPTIONS = ['10', '25'];

export const ScenarioForm: React.FC<ScenarioFormProps> = ({
  mode,
  initialValues = {},
  loading = false,
  error = null,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState(initialValues.name || '');
  const [difficulty, setDifficulty] = useState(initialValues.difficulty || '');
  const [size, setSize] = useState(initialValues.size || '');
  const [isActive, setIsActive] = useState(initialValues.is_active ?? true);
  const [showErrors, setShowErrors] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!name.trim() || !difficulty || !size) return;
    onSubmit({
      name: name.trim(),
      difficulty,
      size,
      is_active: isActive,
    });
  };

  const nameError = showErrors && !name.trim() ? 'Name is required' : '';
  const difficultyError = showErrors && !difficulty ? 'Difficulty is required' : '';
  const sizeError = showErrors && !size ? 'Size is required' : '';

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">
          {mode === 'add' ? 'Add Scenario' : 'Edit Scenario'}
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
            placeholder="Enter scenario name"
            disabled={loading}
          />
          {nameError && <div className="text-red-400 text-xs mt-1">{nameError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="scenario-difficulty" className="block text-sm font-medium text-slate-300 mb-2">
            Difficulty
          </label>
          <select
            id="scenario-difficulty"
            value={difficulty}
            onChange={e => setDifficulty(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select difficulty</option>
            {DIFFICULTY_OPTIONS.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {difficultyError && <div className="text-red-400 text-xs mt-1">{difficultyError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="scenario-size" className="block text-sm font-medium text-slate-300 mb-2">
            Size
          </label>
          <select
            id="scenario-size"
            value={size}
            onChange={e => setSize(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select size</option>
            {SIZE_OPTIONS.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {sizeError && <div className="text-red-400 text-xs mt-1">{sizeError}</div>}
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
          <p className="text-xs text-slate-400 mt-1">
            Active scenarios are available for creating raids
          </p>
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !name.trim() || !difficulty || !size} 
            data-testid="scenario-form-submit"
          >
            {loading ? (mode === 'add' ? 'Adding...' : 'Saving...') : (mode === 'add' ? 'Add Scenario' : 'Save Changes')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 