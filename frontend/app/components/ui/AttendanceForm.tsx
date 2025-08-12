import React, { useState } from 'react';
import { Button, Card } from './';
import type { Raid, Toon, AttendanceStatus } from '../../api/types';

interface AttendanceFormProps {
  raids: Raid[];
  toons: Toon[];
  loading?: boolean;
  error?: string | null;
  onSubmit: (values: { raid_id: number; toon_id: number; status: AttendanceStatus; notes?: string; benched_note?: string }) => void;
  onCancel: () => void;
  initialValues?: Partial<{ raid_id: number; toon_id: number; status: AttendanceStatus; notes: string; benched_note: string }>;
  isEditing?: boolean;
}

export const AttendanceForm: React.FC<AttendanceFormProps> = ({
  raids,
  toons,
  loading = false,
  error = null,
  onSubmit,
  onCancel,
  initialValues = {},
  isEditing = false,
}) => {
  const [raidId, setRaidId] = useState<number | ''>(initialValues.raid_id ?? (raids.length > 0 ? raids[0].id : ''));
  const [toonId, setToonId] = useState<number | ''>(initialValues.toon_id ?? (toons.length > 0 ? toons[0].id : ''));
  const [status, setStatus] = useState<AttendanceStatus>(initialValues.status ?? 'present');
  const [notes, setNotes] = useState(initialValues.notes || '');
  const [benchedNote, setBenchedNote] = useState(initialValues.benched_note || '');
  const [showErrors, setShowErrors] = useState(false);

  const noRaids = raids.length === 0;
  const noToons = toons.length === 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!raidId || !toonId) return;
    onSubmit({
      raid_id: Number(raidId),
      toon_id: Number(toonId),
      status: status,
      notes: notes.trim() || undefined,
      benched_note: status === 'benched' ? (benchedNote.trim() || undefined) : undefined,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const raidError = showErrors && !raidId ? 'Raid is required' : '';
  const toonError = showErrors && !toonId ? 'Toon is required' : '';

  // Helper function to format raid display
  const formatRaidDisplay = (raid: Raid) => {
    const date = new Date(raid.scheduled_at);
    return `Raid #${raid.id} - ${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  return (
    <Card variant="elevated" className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold text-white mb-4">{isEditing ? 'Edit Attendance' : 'Add Attendance'}</h2>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        {(noRaids || noToons) && (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 mb-4">
            <p className="text-yellow-400 text-sm">You must have at least one raid and one toon to create an attendance record.</p>
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="attendance-raid" className="block text-sm font-medium text-slate-300 mb-2">Raid</label>
          <select
            id="attendance-raid"
            value={raidId}
            onChange={e => setRaidId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading || noRaids}
          >
            <option value="">Select a raid</option>
            {raids.map(raid => (
              <option key={raid.id} value={raid.id}>{formatRaidDisplay(raid)}</option>
            ))}
          </select>
          {raidError && <div className="text-red-400 text-xs mt-1">{raidError}</div>}
        </div>
        <div className="mb-4">
          <label htmlFor="attendance-toon" className="block text-sm font-medium text-slate-300 mb-2">Toon</label>
          <select
            id="attendance-toon"
            value={toonId}
            onChange={e => setToonId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            disabled={loading || noToons}
          >
            <option value="">Select a toon</option>
            {toons.map(toon => (
              <option key={toon.id} value={toon.id}>{toon.username} ({toon.class} - {toon.role})</option>
            ))}
          </select>
          {toonError && <div className="text-red-400 text-xs mt-1">{toonError}</div>}
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-300 mb-2">Status</label>
          <div className="flex flex-col space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                value="present"
                checked={status === 'present'}
                onChange={() => setStatus('present')}
                className="mr-2 text-amber-500 focus:ring-amber-500"
                disabled={loading}
              />
              <span className="text-green-400">Present</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="absent"
                checked={status === 'absent'}
                onChange={() => setStatus('absent')}
                className="mr-2 text-amber-500 focus:ring-amber-500"
                disabled={loading}
              />
              <span className="text-red-400">Absent</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="benched"
                checked={status === 'benched'}
                onChange={() => setStatus('benched')}
                className="mr-2 text-amber-500 focus:ring-amber-500"
                disabled={loading}
              />
              <span className="text-yellow-400">Benched</span>
            </label>
          </div>
        </div>
        <div className="mb-4">
          <label htmlFor="attendance-notes" className="block text-sm font-medium text-slate-300 mb-2">
            Notes <span className="text-slate-500">(Optional)</span>
          </label>
          <textarea
            id="attendance-notes"
            value={notes}
            onChange={e => setNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="Add notes about attendance (e.g., 'On time', 'Late', 'No show')"
            disabled={loading}
            onKeyPress={handleKeyPress}
          />
        </div>
        {status === 'benched' && (
          <div className="mb-6">
            <label htmlFor="attendance-benched-notes" className="block text-sm font-medium text-slate-300 mb-2">
              Benched Note <span className="text-slate-500">(Optional)</span>
            </label>
            <textarea
              id="attendance-benched-notes"
              value={benchedNote}
              onChange={e => setBenchedNote(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder="Add note about why player is benched (e.g., 'Available for fill', 'Gear issues')"
              disabled={loading}
              onKeyPress={handleKeyPress}
            />
          </div>
        )}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading || !raidId || !toonId || noRaids || noToons} data-testid="attendance-form-submit">
            {loading ? (isEditing ? 'Updating...' : 'Adding...') : (isEditing ? 'Update Attendance' : 'Add Attendance')}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 