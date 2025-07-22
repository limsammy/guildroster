import React from 'react';
import { Button, Card } from './';
import type { WarcraftLogsProcessingResult } from '../../api/types';

interface WarcraftLogsResultsProps {
  result: WarcraftLogsProcessingResult;
  onProceed: () => void;
  onCancel: () => void;
  loading?: boolean;
  onAddUnknownParticipant?: (participant: any) => void;
}

export const WarcraftLogsResults: React.FC<WarcraftLogsResultsProps> = ({
  result,
  onProceed,
  onCancel,
  loading = false,
  onAddUnknownParticipant,
}) => {
  const getClassColor = (className: string) => {
    const colors: Record<string, string> = {
      'Death Knight': 'text-red-400',
      'Warrior': 'text-orange-400',
      'Druid': 'text-orange-500',
      'Paladin': 'text-pink-400',
      'Monk': 'text-green-400',
      'Rogue': 'text-yellow-400',
      'Hunter': 'text-green-500',
      'Mage': 'text-blue-400',
      'Warlock': 'text-purple-400',
      'Priest': 'text-white',
      'Shaman': 'text-blue-500',
      'Demon Hunter': 'text-purple-500',
      'Evoker': 'text-green-300',
    };
    return colors[className] || 'text-slate-300';
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const presentCount = result.matched_participants.filter(p => p.is_present).length;
  const absentCount = result.matched_participants.filter(p => !p.is_present).length;

  return (
    <Card variant="elevated" className="w-full max-w-[1200px] min-w-[900px] mx-auto max-h-[90vh] flex flex-col">
      <div className="p-6 flex-1 overflow-hidden flex flex-col">
        {/* Info Blurb at the Top */}
        <div className="mb-4 flex items-center gap-2 bg-blue-500/10 border border-blue-400/30 text-blue-200 rounded-lg px-4 py-2">
          <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-400 text-white font-bold text-xs">i</span>
          <span>
            Scroll down to add any participants from the report who aren't recognized as existing characters. If a name doesn't match but should, you can link it to an existing character.
          </span>
        </div>
        <h2 className="text-xl font-bold text-white mb-4">
          WarcraftLogs Report Analysis
        </h2>

        {/* Report Metadata */}
        <div className="bg-slate-800/50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-white mb-2">
            {result.report_metadata.title}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-300">
            <div>
              <span className="font-medium">Zone:</span> {result.report_metadata.zone.name}
            </div>
            <div>
              <span className="font-medium">Start:</span> {formatDate(result.report_metadata.startTime)}
            </div>
            <div>
              <span className="font-medium">Owner:</span> {result.report_metadata.owner.name}
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 flex-shrink-0">
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
            <div className="text-2xl font-bold text-green-400">{presentCount}</div>
            <div className="text-sm text-green-300">Present</div>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <div className="text-2xl font-bold text-red-400">{absentCount}</div>
            <div className="text-sm text-red-300">Absent</div>
          </div>
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
            <div className="text-2xl font-bold text-amber-400">{result.participants.length}</div>
            <div className="text-sm text-amber-300">Total</div>
          </div>
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto min-h-0">
          {/* Matched Participants */}
          <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">
            Team Characters ({result.matched_participants.length})
          </h3>
          {result.matched_participants.length === 0 ? (
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <p className="text-blue-300 text-sm">
                No existing team characters found. All participants from the report will need to be assigned to new or existing characters.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {result.matched_participants.map((matched, index) => (
              <div
                key={index}
                className={`flex items-center justify-between p-3 rounded-lg border ${
                  matched.is_present
                    ? 'bg-green-500/10 border-green-500/20'
                    : 'bg-red-500/10 border-red-500/20'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="text-white font-medium">
                      {matched.toon.username}
                    </div>
                    <div className={`text-sm ${getClassColor(matched.toon.class)}`}>
                      {matched.toon.class} - {matched.toon.role}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-medium ${matched.is_present ? 'text-green-400' : 'text-red-400'}`}>
                    {matched.is_present ? 'Present' : 'Absent'}
                  </div>
                  <div className="text-xs text-slate-400">
                    {matched.notes}
                  </div>
                </div>
              </div>
            ))}
            </div>
          )}
        </div>

        {/* Unknown Participants Notice */}
        {result.unknown_participants.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3">
              Unknown Participants ({result.unknown_participants.length})
            </h3>
            <div className="mb-2 text-xs text-slate-300">
              Scroll down to add any participants from the report who aren't recognized as existing characters. If a name doesn't match but should, you can link it to an existing character.
            </div>
            <div className="space-y-2">
              {result.unknown_participants.map((unknown, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg border bg-yellow-500/10 border-yellow-500/20">
                  <div>
                    <div className="text-white font-medium">{unknown.participant.name}</div>
                    <div className={`text-sm ${getClassColor(unknown.participant.class)}`}>{unknown.participant.class} - {unknown.participant.role}</div>
                  </div>
                  <div className="flex gap-2">
                    {onAddUnknownParticipant && (
                      <Button
                        type="button"
                        variant="primary"
                        size="sm"
                        className="ml-2"
                        onClick={() => onAddUnknownParticipant(unknown)}
                      >
                        Add
                      </Button>
                    )}
                    {/* Link button for name mismatch handling (UI only) */}
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      className="ml-2"
                      // onClick: open link modal (to be implemented)
                    >
                      Link
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-2 flex-shrink-0 p-6 pt-0 mt-6">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="button" variant="primary" onClick={onProceed} disabled={loading}>
          {loading ? 'Creating Raid...' : 'Create Raid with Attendance'}
        </Button>
      </div>
    </div>
  </Card>
);
}; 