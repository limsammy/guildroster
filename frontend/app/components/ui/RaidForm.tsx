import React, { useState, useEffect } from 'react';
import { Button, Card, WarcraftLogsResults } from './';
import type { Team, Scenario, ScenarioVariation, WarcraftLogsProcessingResult } from '../../api/types';
import { RaidService } from '../../api/raids';
import { ToonForm } from './ToonForm';
import { TeamService } from '../../api/teams';
import { ToonService } from '../../api/toons';

interface RaidFormProps {
  teams: Team[];
  scenarios: Scenario[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { warcraftlogs_url: string; team_id: number; scenario_name: string; scenario_difficulty: string; scenario_size: string }) => void;
  onCancel: () => void;
  initialValues?: Partial<{ warcraftlogs_url: string; team_id: number; scenario_name: string; scenario_difficulty: string; scenario_size: string }>;
  isEditing?: boolean;
}

type FormStep = 'form' | 'processing' | 'results';

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
  const [scenarioName, setScenarioName] = useState(initialValues.scenario_name || '');
  const [scenarioDifficulty, setScenarioDifficulty] = useState(initialValues.scenario_difficulty || '');
  const [scenarioSize, setScenarioSize] = useState(initialValues.scenario_size || '');
  const [showErrors, setShowErrors] = useState(false);
  
  // WarcraftLogs processing state
  const [currentStep, setCurrentStep] = useState<FormStep>('form');
  const [processingResult, setProcessingResult] = useState<WarcraftLogsProcessingResult | null>(null);
  const [processingLoading, setProcessingLoading] = useState(false);
  const [processingError, setProcessingError] = useState<string | null>(null);

  // Get all scenario variations
  const [allVariations, setAllVariations] = useState<ScenarioVariation[]>([]);
  const [variationsLoading, setVariationsLoading] = useState(false);

  const [showToonForm, setShowToonForm] = useState(false);
  const [toonFormLoading, setToonFormLoading] = useState(false);
  const [toonFormError, setToonFormError] = useState<string | null>(null);
  const [toonFormInitialValues, setToonFormInitialValues] = useState<any>(null);
  const [allTeams, setAllTeams] = useState<Team[]>(teams);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const noTeams = teams.length === 0;
  const noScenarios = scenarios.length === 0;

  // Load scenario variations when component mounts
  useEffect(() => {
    const loadVariations = async () => {
      if (scenarios.length === 0) return;
      
      setVariationsLoading(true);
      try {
        const variations = await RaidService.getAllScenarioVariations();
        setAllVariations(variations);
      } catch (err) {
        console.error('Failed to load scenario variations:', err);
      } finally {
        setVariationsLoading(false);
      }
    };

    loadVariations();
  }, [scenarios]);

  // Fetch all teams if not already loaded
  useEffect(() => {
    if (allTeams.length === 0) {
      TeamService.getTeams().then(setAllTeams);
    }
  }, [allTeams.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!teamId || !scenarioName || !scenarioDifficulty || !scenarioSize) return;

    // If no WarcraftLogs URL, proceed with normal form submission
    if (!warcraftlogsUrl.trim()) {
      onSubmit({
        warcraftlogs_url: '',
        team_id: Number(teamId),
        scenario_name: scenarioName,
        scenario_difficulty: scenarioDifficulty,
        scenario_size: scenarioSize,
      });
      return;
    }

    // Process WarcraftLogs URL
    await processWarcraftLogs();
  };

  const processWarcraftLogs = async () => {
    if (!warcraftlogsUrl.trim() || !teamId) return;

    setProcessingLoading(true);
    setProcessingError(null);
    setCurrentStep('processing');

    try {
      const result = await RaidService.processWarcraftLogs(warcraftlogsUrl.trim(), Number(teamId));
      setProcessingResult(result);
      setCurrentStep('results');
    } catch (err: any) {
      // Handle different types of error responses
      let errorMessage = 'Failed to process WarcraftLogs report';
      if (err.response?.data?.detail) {
        errorMessage = typeof err.response.data.detail === 'string' 
          ? err.response.data.detail 
          : 'Invalid request format';
      } else if (err.message) {
        errorMessage = err.message;
      }
      setProcessingError(errorMessage);
      setCurrentStep('form');
    } finally {
      setProcessingLoading(false);
    }
  };

  const handleProceedWithRaid = async () => {
    if (!processingResult) return;

    setProcessingLoading(true);
    try {
      // Submit the raid creation
      onSubmit({
        warcraftlogs_url: warcraftlogsUrl.trim(),
        team_id: Number(teamId),
        scenario_name: scenarioName,
        scenario_difficulty: scenarioDifficulty,
        scenario_size: scenarioSize,
      });
    } catch (err) {
      console.error('Failed to create raid:', err);
    } finally {
      setProcessingLoading(false);
    }
  };

  const handleBackToForm = () => {
    setCurrentStep('form');
    setProcessingResult(null);
    setProcessingError(null);
  };

  const handleAddUnknownParticipant = (unknown: any) => {
    setToonFormInitialValues({
      username: unknown.participant.name,
      class: unknown.participant.class,
      role: unknown.participant.role,
      team_ids: teamId ? [Number(teamId)] : [],
    });
    setShowToonForm(true);
  };

  const handleToonFormSubmit = async (values: any) => {
    setToonFormLoading(true);
    setToonFormError(null);
    try {
      await ToonService.createToon(values);
      setShowToonForm(false);
      setSuccessMessage('Character added!');
      // Auto-hide success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
      // Re-run WarcraftLogs processing to refresh results
      await processWarcraftLogs();
    } catch (err: any) {
      setToonFormError(err.response?.data?.detail || 'Failed to create toon');
    } finally {
      setToonFormLoading(false);
    }
  };

  const handleToonFormCancel = () => {
    setShowToonForm(false);
    setToonFormInitialValues(null);
    setToonFormError(null);
  };

  // Show processing step
  if (currentStep === 'processing') {
    return (
      <Card variant="elevated" className="max-w-md mx-auto p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-white mb-2">Processing WarcraftLogs Report</h3>
          <p className="text-slate-400 text-sm">Extracting participant data and fight information...</p>
        </div>
      </Card>
    );
  }

  // Show results step
  if (currentStep === 'results' && processingResult) {
    return (
      <>
        {successMessage && (
          <div className="fixed top-8 left-1/2 transform -translate-x-1/2 z-50">
            <div className="bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg animate-fade-in">
              {successMessage}
            </div>
          </div>
        )}
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="w-full max-w-[1200px] flex justify-center items-center">
            <WarcraftLogsResults
              result={processingResult}
              onProceed={handleProceedWithRaid}
              onCancel={handleBackToForm}
              loading={processingLoading}
              onAddUnknownParticipant={handleAddUnknownParticipant}
            />
          </div>
        </div>
        {showToonForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="w-full max-w-md">
              <ToonForm
                mode="add"
                teams={allTeams}
                initialValues={toonFormInitialValues}
                loading={toonFormLoading}
                error={toonFormError}
                onSubmit={handleToonFormSubmit}
                onCancel={handleToonFormCancel}
              />
            </div>
          </div>
        )}
      </>
    );
  }

  // Show main form
  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">{isEditing ? 'Edit Raid' : 'Add Raid'}</h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{typeof error === 'string' ? error : 'An error occurred'}</p>
          </div>
        )}
        {processingError && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{typeof processingError === 'string' ? processingError : 'An error occurred'}</p>
          </div>
        )}
        {(noTeams || noScenarios) && (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 mb-4">
            <p className="text-yellow-400 text-sm">You must have at least one team and one scenario template to create a raid.</p>
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
          {warcraftlogsUrl.trim() && (
            <div className="text-amber-400 text-xs mt-1">
              ⚡ This will automatically process attendance from the WarcraftLogs report
            </div>
          )}
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
        </div>
        <div className="mb-6">
          <label htmlFor="raid-scenario" className="block text-sm font-medium text-slate-300 mb-2">Scenario Variation</label>
          <select
            id="raid-scenario"
            value={`${scenarioName}|${scenarioDifficulty}|${scenarioSize}`}
            onChange={e => {
              const [name, difficulty, size] = e.target.value.split('|');
              setScenarioName(name || '');
              setScenarioDifficulty(difficulty || '');
              setScenarioSize(size || '');
            }}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading || noScenarios || variationsLoading}
          >
            <option value="">Select a scenario variation</option>
            {allVariations.map(variation => (
              <option key={variation.variation_id} value={variation.variation_id}>
                {variation.display_name}
              </option>
            ))}
          </select>
          {variationsLoading && (
            <div className="text-slate-400 text-xs mt-1">Loading scenario variations...</div>
          )}
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !teamId || !scenarioName || !scenarioDifficulty || !scenarioSize || noTeams || noScenarios} 
            data-testid="raid-form-submit"
          >
            {loading ? (isEditing ? 'Updating...' : 'Adding...') : (isEditing ? 'Update Raid' : 'Add Raid')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 