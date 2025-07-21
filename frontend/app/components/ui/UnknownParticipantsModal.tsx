import React, { useState, useEffect } from 'react';
import { Button, Card } from './';
import type { UnknownParticipant, Member, ToonCreate } from '../../api/types';
import { MemberService } from '../../api/members';
import { ToonService } from '../../api/toons';

interface UnknownParticipantsModalProps {
  unknownParticipants: UnknownParticipant[];
  teamId: number;
  guildId: number;
  onComplete: (assignments: Array<{ participant: UnknownParticipant; memberId: number; toonData: ToonCreate }>) => void;
  onCancel: () => void;
  isOpen: boolean;
}

export const UnknownParticipantsModal: React.FC<UnknownParticipantsModalProps> = ({
  unknownParticipants,
  teamId,
  guildId,
  onComplete,
  onCancel,
  isOpen,
}) => {
  const [assignments, setAssignments] = useState<Array<{ participant: UnknownParticipant; memberId: number | ''; toonData: Partial<ToonCreate> }>>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load members when modal opens
  useEffect(() => {
    if (isOpen && members.length === 0) {
      loadMembers();
    }
  }, [isOpen, members.length]);

  // Initialize assignments when unknown participants change
  useEffect(() => {
    if (unknownParticipants.length > 0) {
      setAssignments(
        unknownParticipants.map(participant => ({
          participant,
          memberId: '',
          toonData: {
            username: participant.participant.name,
            class: participant.participant.class,
            role: participant.participant.role || 'DPS', // Use role from WarcraftLogs
            is_main: false,
            member_id: 0,
            team_ids: [teamId],
          },
        }))
      );
    }
  }, [unknownParticipants, teamId]);

  const loadMembers = async () => {
    try {
      setLoading(true);
      const guildMembers = await MemberService.getMembersByGuild(guildId);
      setMembers(guildMembers);
    } catch (err) {
      setError('Failed to load members');
      console.error('Error loading members:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateAssignment = (index: number, field: 'memberId' | 'toonData', value: any) => {
    setAssignments(prev => prev.map((assignment, i) => {
      if (i === index) {
        if (field === 'memberId') {
          return { ...assignment, memberId: value, toonData: { ...assignment.toonData, member_id: value ? Number(value) : 0 } };
        } else {
          return { ...assignment, toonData: { ...assignment.toonData, ...value } };
        }
      }
      return assignment;
    }));
  };

  const handleComplete = () => {
    const validAssignments = assignments.filter(a => a.memberId && a.toonData.member_id);
    if (validAssignments.length !== unknownParticipants.length) {
      setError('Please assign all participants to members');
      return;
    }

    const completedAssignments = validAssignments.map(assignment => ({
      participant: assignment.participant,
      memberId: Number(assignment.memberId),
      toonData: assignment.toonData as ToonCreate,
    }));

    onComplete(completedAssignments);
  };

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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card variant="elevated" className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-xl font-bold text-white mb-4">
            Unknown Participants Found ({unknownParticipants.length})
          </h2>
          <p className="text-slate-300 mb-6">
            The following participants were found in the WarcraftLogs report but are not in your team. 
            Please assign them to existing members or create new members.
          </p>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            {assignments.map((assignment, index) => (
              <div key={index} className="border border-slate-600 rounded-lg p-4">
                <div className="flex items-center gap-4 mb-3">
                  <div className="flex-1">
                    <h3 className="text-white font-medium">
                      {assignment.participant.participant.name}
                    </h3>
                    <p className={`text-sm ${getClassColor(assignment.participant.participant.class)}`}>
                      {assignment.participant.participant.class}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Assign to Member
                    </label>
                    <select
                      value={assignment.memberId}
                      onChange={(e) => updateAssignment(index, 'memberId', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      disabled={loading}
                    >
                      <option value="">Select a member</option>
                      {members.map(member => (
                        <option key={member.id} value={member.id}>
                          {member.display_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Role
                    </label>
                    <select
                      value={assignment.toonData.role}
                      onChange={(e) => updateAssignment(index, 'toonData', { role: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    >
                      <option value="DPS">DPS</option>
                      <option value="Healer">Healer</option>
                      <option value="Tank">Tank</option>
                    </select>
                  </div>
                </div>

                <div className="mt-3">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={assignment.toonData.is_main}
                      onChange={(e) => updateAssignment(index, 'toonData', { is_main: e.target.checked })}
                      className="rounded border-slate-600 bg-slate-800 text-amber-500 focus:ring-amber-500"
                    />
                    <span className="text-sm text-slate-300">Main character</span>
                  </label>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-2 mt-6">
            <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
            <Button 
              type="button" 
              variant="primary" 
              onClick={handleComplete}
              disabled={loading || assignments.some(a => !a.memberId)}
            >
              {loading ? 'Processing...' : 'Complete Assignment'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}; 