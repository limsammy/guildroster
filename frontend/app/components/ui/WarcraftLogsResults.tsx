import React, { useState, useEffect } from 'react';
import { Button, Card } from './';
import type { WarcraftLogsProcessingResult } from '../../api/types';

interface WarcraftLogsResultsProps {
  result: WarcraftLogsProcessingResult;
  onProceed: (updatedResult?: WarcraftLogsProcessingResult) => void;
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
  const [participants, setParticipants] = useState(result.matched_participants);
  const [updatedResult, setUpdatedResult] = useState(result);
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

  const presentCount = participants.filter(p => p.status === 'present').length;
  const absentCount = participants.filter(p => p.status === 'absent').length;
  const benchedCount = participants.filter(p => p.status === 'benched').length;

  // Initialize participants with status if not already set
  useEffect(() => {
    const initializedParticipants = result.matched_participants.map(p => ({
      ...p,
      status: p.is_present ? 'present' : 'absent',
      benched_note: ''
    }));
    setParticipants(initializedParticipants);
    
    // Also update the result object with initialized participants
    const newResult = {
      ...result,
      matched_participants: initializedParticipants
    };
    setUpdatedResult(newResult);
  }, [result.matched_participants]);

  const handleStatusChange = (index: number, newStatus: 'present' | 'absent' | 'benched') => {
    const updatedParticipants = [...participants];
    updatedParticipants[index] = {
      ...updatedParticipants[index],
      status: newStatus,
      is_present: newStatus === 'present'
    };
    setParticipants(updatedParticipants);
    
    // Update the result object
    const newResult = {
      ...result,
      matched_participants: updatedParticipants
    };
    setUpdatedResult(newResult);
  };

  const handleBenchedNoteChange = (index: number, note: string) => {
    const updatedParticipants = [...participants];
    updatedParticipants[index] = {
      ...updatedParticipants[index],
      benched_note: note
    };
    setParticipants(updatedParticipants);
    
    // Update the result object
    const newResult = {
      ...result,
      matched_participants: updatedParticipants
    };
    setUpdatedResult(newResult);
  };

  const handleProceed = () => {
    onProceed(updatedResult);
  };

  return (
    <Card variant="elevated" className="w-full max-w-[1200px] mx-auto max-h-[90vh] flex flex-col">
      <div className="p-3 sm:p-6 flex-1 overflow-hidden flex flex-col">
        {/* Info Blurb at the Top - Collapsible on Mobile */}
        <div className="mb-4 group relative">
          <div className="flex items-start gap-2 bg-blue-500/10 border border-blue-400/30 text-blue-200 rounded-lg px-3 py-2 sm:px-4 cursor-help">
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-400 text-white font-bold text-xs flex-shrink-0 mt-0.5">i</span>
            <span className="text-sm">
              <span className="sm:hidden">Tap for info about unrecognized participants</span>
              <span className="hidden sm:inline">Scroll down to add any participants from the report who aren't recognized as existing characters. If a name doesn't match but should, you can link it to an existing character.</span>
            </span>
          </div>
          {/* Mobile tooltip */}
          <div className="absolute top-full left-0 right-0 mt-2 bg-blue-500/95 border border-blue-400/30 text-blue-100 rounded-lg p-3 text-sm z-10 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity duration-200 pointer-events-none sm:hidden">
            Scroll down to add any participants from the report who aren't recognized as existing characters. If a name doesn't match but should, you can link it to an existing character.
          </div>
        </div>
        <h2 className="text-lg sm:text-xl font-bold text-white mb-4">
          WarcraftLogs Report Analysis
        </h2>

        {/* Report Metadata */}
        <div className="bg-slate-800/50 rounded-lg p-3 sm:p-4 mb-4 sm:mb-6">
          <h3 className="text-base sm:text-lg font-semibold text-white mb-2">
            {result.report_metadata.title}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-4 text-xs sm:text-sm text-slate-300">
            <div>
              <span className="font-medium">Zone:</span> {result.report_metadata.zone.name}
            </div>
            <div>
              <span className="font-medium">Start:</span> {formatDate(result.report_metadata.startTime)}
            </div>
            <div className="sm:col-span-2 lg:col-span-1">
              <span className="font-medium">Owner:</span> {result.report_metadata.owner.name}
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-1 sm:gap-4 mb-3 sm:mb-6 flex-shrink-0">
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-1.5 sm:p-3">
            <div className="text-base sm:text-2xl font-bold text-green-400">{presentCount}</div>
            <div className="text-xs text-green-300">Present</div>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-1.5 sm:p-3">
            <div className="text-base sm:text-2xl font-bold text-red-400">{absentCount}</div>
            <div className="text-xs text-red-300">Absent</div>
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-1.5 sm:p-3">
            <div className="text-base sm:text-2xl font-bold text-yellow-400">{benchedCount}</div>
            <div className="text-xs text-yellow-300">Benched</div>
          </div>
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-1.5 sm:p-3">
            <div className="text-base sm:text-2xl font-bold text-amber-400">{result.participants.length}</div>
            <div className="text-xs text-amber-300">Total</div>
          </div>
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto min-h-0">
          {/* Matched Participants */}
          <div className="mb-3 sm:mb-6">
          <h3 className="text-base sm:text-lg font-semibold text-white mb-2 sm:mb-3">
            Team Characters ({result.matched_participants.length})
          </h3>
          {result.matched_participants.length === 0 ? (
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 sm:p-4">
              <p className="text-blue-300 text-xs sm:text-sm">
                No existing team characters found. All participants from the report will need to be assigned to new or existing characters.
              </p>
            </div>
          ) : (
            <div className="space-y-1.5 sm:space-y-2">
              {participants.map((matched, index) => (
              <div
                key={index}
                className={`p-2 sm:p-3 rounded-lg border ${
                  matched.status === 'present'
                    ? 'bg-green-500/10 border-green-500/20'
                    : matched.status === 'benched'
                    ? 'bg-yellow-500/10 border-yellow-500/20'
                    : 'bg-red-500/10 border-red-500/20'
                }`}
              >
                {/* Character Info */}
                <div className="mb-2 sm:mb-3">
                  <div className="text-white font-medium truncate">
                    {matched.toon.username}
                  </div>
                  <div className={`text-xs ${getClassColor(matched.toon.class)}`}>
                    {matched.toon.class} - {matched.toon.role}
                  </div>
                </div>
                
                {/* Status Selection */}
                <div className="mb-2 sm:mb-3">
                  <div className="text-xs text-slate-400 mb-1">Status:</div>
                  <div className="flex gap-1 flex-wrap">
                    <button
                      onClick={() => handleStatusChange(index, 'present')}
                      className={`px-2 py-1 text-xs rounded ${
                        matched.status === 'present'
                          ? 'bg-green-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      Present
                    </button>
                    <button
                      onClick={() => handleStatusChange(index, 'absent')}
                      className={`px-2 py-1 text-xs rounded ${
                        matched.status === 'absent'
                          ? 'bg-red-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      Absent
                    </button>
                    <button
                      onClick={() => handleStatusChange(index, 'benched')}
                      className={`px-2 py-1 text-xs rounded ${
                        matched.status === 'benched'
                          ? 'bg-yellow-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      Benched
                    </button>
                  </div>
                </div>
                
                {/* Benched Note Input */}
                {matched.status === 'benched' && (
                  <div className="mb-2 sm:mb-3">
                    <div className="text-xs text-slate-400 mb-1">Note:</div>
                    <input
                      type="text"
                      value={matched.benched_note || ''}
                      onChange={(e) => handleBenchedNoteChange(index, e.target.value)}
                      placeholder="Benched reason..."
                      className="w-full px-2 py-1 text-xs bg-slate-800 border border-slate-600 rounded text-white focus:outline-none focus:ring-1 focus:ring-yellow-500"
                    />
                  </div>
                )}
                
                {/* Original Notes */}
                {matched.notes && (
                  <div>
                    <div className="text-xs text-slate-400">
                      {matched.notes}
                    </div>
                  </div>
                )}
              </div>
            ))}
            </div>
          )}
        </div>

        {/* Unknown Participants Notice */}
        {result.unknown_participants.length > 0 && (
          <div className="mb-3 sm:mb-6">
            <h3 className="text-base sm:text-lg font-semibold text-white mb-2 sm:mb-3">
              Unknown Participants ({result.unknown_participants.length})
            </h3>
            <div className="mb-2 text-xs text-slate-300">
              Scroll down to add any participants from the report who aren't recognized as existing characters. If a name doesn't match but should, you can link it to an existing character.
            </div>
            <div className="space-y-1.5 sm:space-y-2">
              {result.unknown_participants.map((unknown, idx) => (
                <div key={idx} className="p-2 sm:p-3 rounded-lg border bg-yellow-500/10 border-yellow-500/20">
                  <div className="mb-2 sm:mb-3">
                    <div className="text-white font-medium truncate">{unknown.participant.name}</div>
                    <div className={`text-xs ${getClassColor(unknown.participant.class)}`}>{unknown.participant.class} - {unknown.participant.role}</div>
                  </div>
                  <div className="flex gap-2">
                    {onAddUnknownParticipant && (
                      <Button
                        type="button"
                        variant="primary"
                        size="sm"
                        className="flex-1"
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
                      className="flex-1"
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
      <div className="flex flex-col sm:flex-row justify-end gap-2 flex-shrink-0 p-4 sm:p-6 pt-0 mt-4 sm:mt-6">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={loading} className="w-full sm:w-auto">
          Cancel
        </Button>
        <Button type="button" variant="primary" onClick={handleProceed} disabled={loading} className="w-full sm:w-auto">
          {loading ? 'Creating Raid...' : 'Create Raid with Attendance'}
        </Button>
      </div>
    </div>
  </Card>
);
}; 