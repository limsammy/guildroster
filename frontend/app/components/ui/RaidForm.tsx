import React, { useState, useEffect } from 'react';
import { Button, Card } from './';
import type { Team, Scenario } from '../../api/types';

interface RaidFormProps {
  teams: Team[];
  scenarios: Scenario[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { warcraftlogs_url: string; team_id: number; scenario_id: number }) => void;
  onCancel: () => void;
  initialValues?: Partial<{ warcraftlogs_url: string; team_id: number; scenario_id: number }>;
  isEditing?: boolean;
}

export const RaidForm: React.FC<RaidFormProps> = ({
  teams,
  scenarios,
  loading = false,
  error = null,
  onSubmit,
  onCancel,
  initialValues = {},
  isEditing = false,
}) => {
  const [warcraftlogsUrl, setWarcraftlogsUrl] = useState(initialValues.warcraftlogs_url || '');
  const [teamId, setTeamId] = useState<number | ''>(initialValues.team_id ?? (teams.length > 0 ? teams[0].id : ''));
  const [scenarioId, setScenarioId] = useState<number | ''>(initialValues.scenario_id ?? (scenarios.length > 0 ? scenarios[0].id : ''));
  const [showErrors, setShowErrors] = useState(false);

  const noTeams = teams.length === 0;
  const noScenarios = scenarios.length === 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!teamId || !scenarioId) return;
    onSubmit({
      warcraftlogs_url: warcraftlogsUrl.trim() || '',
      team_id: Number(teamId),
      scenario_id: Number(scenarioId),
    });
  };

  const urlError = showErrors && warcraftlogsUrl.trim() && !warcraftlogsUrl.includes('warcraftlogs.com/reports/') ? 'Invalid WarcraftLogs URL format' : '';
  const teamError = showErrors && !teamId ? 'Team is required' : '';
  const scenarioError = showErrors && !scenarioId ? 'Scenario is required' : '';

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">{isEditing ? 'Edit Raid' : 'Add Raid'}</h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        {(noTeams || noScenarios) && (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 mb-4">
            <p className="text-yellow-400 text-sm">You must have at least one team and one scenario to create a raid.</p>
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="warcraftlogs-url" className="block text-sm font-medium text-slate-300 mb-2">
            WarcraftLogs URL <span className="text-slate-500">(Optional)</span>
          </label>
          <input
            id="warcraftlogs-url"
            type="text"
            value={warcraftlogsUrl}
            onChange={e => setWarcraftlogsUrl(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="Paste WarcraftLogs report URL here (optional)"
            disabled={loading || noTeams || noScenarios}
          />
          {urlError && <div className="text-red-400 text-xs mt-1">{urlError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="raid-team" className="block text-sm font-medium text-slate-300 mb-2">Team</label>
          <select
            id="raid-team"
            value={teamId}
            onChange={e => setTeamId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading || noTeams}
          >
            <option value="">Select a team</option>
            {teams.map(team => (
              <option key={team.id} value={team.id}>{team.name}</option>
            ))}
          </select>
          {teamError && <div className="text-red-400 text-xs mt-1">{teamError}</div>}
        </div>
        <div className="mb-6">
          <label htmlFor="raid-scenario" className="block text-sm font-medium text-slate-300 mb-2">Scenario</label>
          <select
            id="raid-scenario"
            value={scenarioId}
            onChange={e => setScenarioId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading || noScenarios}
          >
            <option value="">Select a scenario</option>
            {scenarios.map(scenario => (
              <option key={scenario.id} value={scenario.id}>{scenario.name} ({scenario.difficulty}, {scenario.size})</option>
            ))}
          </select>
          {scenarioError && <div className="text-red-400 text-xs mt-1">{scenarioError}</div>}
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading || !teamId || !scenarioId || noTeams || noScenarios} data-testid="raid-form-submit">
            {loading ? (isEditing ? 'Updating...' : 'Adding...') : (isEditing ? 'Update Raid' : 'Add Raid')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 