import React, { useState, useEffect } from 'react';
import { Card, Button } from './';
import { AttendanceService } from '../../api/attendance';
import type { BenchedPlayer, Team } from '../../api/types';

interface BenchedPlayersViewProps {
  team: Team;
  onClose: () => void;
}

export const BenchedPlayersView: React.FC<BenchedPlayersViewProps> = ({
  team,
  onClose,
}) => {
  const [benchedPlayers, setBenchedPlayers] = useState<BenchedPlayer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedWeek, setSelectedWeek] = useState<string>('');

  // Get current week (Tuesday 9 AM PST)
  const getCurrentWeek = () => {
    const now = new Date();
    const dayOfWeek = now.getDay(); // 0 = Sunday, 2 = Tuesday
    const daysUntilTuesday = dayOfWeek <= 2 ? 2 - dayOfWeek : 9 - dayOfWeek;
    const nextTuesday = new Date(now);
    nextTuesday.setDate(now.getDate() + daysUntilTuesday);
    nextTuesday.setHours(9, 0, 0, 0); // 9 AM PST
    
    // If we're past Tuesday 9 AM, use this Tuesday, otherwise use last Tuesday
    if (now > nextTuesday) {
      nextTuesday.setDate(nextTuesday.getDate() - 7);
    }
    
    return nextTuesday.toISOString().split('T')[0];
  };

  useEffect(() => {
    setSelectedWeek(getCurrentWeek());
  }, []);

  useEffect(() => {
    if (selectedWeek) {
      fetchBenchedPlayers();
    }
  }, [selectedWeek, team.id]);

  const fetchBenchedPlayers = async () => {
    setLoading(true);
    setError(null);
    try {
      const players = await AttendanceService.getBenchedPlayers(team.id, selectedWeek);
      setBenchedPlayers(players);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch benched players');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present':
        return 'text-green-400';
      case 'absent':
        return 'text-red-400';
      case 'benched':
        return 'text-yellow-400';
      default:
        return 'text-slate-400';
    }
  };

  const getClassColor = (className: string) => {
    const classColors: Record<string, string> = {
      'Death Knight': 'text-red-400',
      'Warrior': 'text-orange-400',
      'Druid': 'text-orange-400',
      'Paladin': 'text-pink-400',
      'Monk': 'text-green-400',
      'Rogue': 'text-yellow-400',
      'Hunter': 'text-green-400',
      'Mage': 'text-blue-400',
      'Warlock': 'text-purple-400',
      'Priest': 'text-white',
      'Shaman': 'text-blue-400',
    };
    return classColors[className] || 'text-slate-400';
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card variant="elevated" className="w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white">
              Benched Players - {team.name}
            </h2>
            <Button type="button" variant="secondary" onClick={onClose}>
              Close
            </Button>
          </div>

          <div className="mb-4">
            <label htmlFor="week-selector" className="block text-sm font-medium text-slate-300 mb-2">
              Week Starting (Tuesday 9 AM PST)
            </label>
            <input
              id="week-selector"
              type="date"
              value={selectedWeek}
              onChange={(e) => setSelectedWeek(e.target.value)}
              className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mx-auto mb-4"></div>
              <p className="text-slate-400">Loading benched players...</p>
            </div>
          ) : benchedPlayers.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-slate-400">No benched players found for this week.</p>
            </div>
          ) : (
            <div className="overflow-y-auto max-h-[60vh]">
              <div className="grid gap-4">
                {benchedPlayers.map((player) => (
                  <div
                    key={player.id}
                    className="bg-slate-800 border border-slate-600 rounded-lg p-4"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-white">
                          {player.toon_username}
                        </span>
                        <span className={`text-sm ${getClassColor(player.toon_class)}`}>
                          {player.toon_class}
                        </span>
                        <span className="text-sm text-slate-400">
                          {player.toon_role}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-slate-400">
                          {formatDate(player.raid_scheduled_at)}
                        </div>
                        <div className="text-xs text-slate-500">
                          {player.raid_scenario_name} ({player.raid_scenario_difficulty} {player.raid_scenario_size})
                        </div>
                      </div>
                    </div>
                    {player.benched_note && (
                      <div className="mt-2 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded text-sm text-yellow-400">
                        <strong>Note:</strong> {player.benched_note}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 text-sm text-slate-400">
            <p>
              <strong>Week Definition:</strong> A week for benched players is defined as Tuesday morning at 9 AM PST until the following Tuesday morning at 9 AM PST.
            </p>
            <p className="mt-1">
              <strong>Current Week:</strong> {selectedWeek ? formatDate(selectedWeek) : 'Loading...'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}; 