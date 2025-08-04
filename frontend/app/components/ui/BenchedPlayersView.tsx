import React, { useState, useEffect } from 'react';
import { Card, Button } from './';
import { TeamService } from '../../api/teams';
import type { Team } from '../../api/types';

interface SimpleBenchedPlayer {
  id: number;
  username: string;
  class_: string;
  role: string;
}

interface BenchedPlayersViewProps {
  team: Team;
  onClose: () => void;
}

export const BenchedPlayersView: React.FC<BenchedPlayersViewProps> = ({
  team,
  onClose,
}) => {
  const [benchedPlayers, setBenchedPlayers] = useState<SimpleBenchedPlayer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBenchedPlayers();
  }, [team.id]);

  const fetchBenchedPlayers = async () => {
    setLoading(true);
    setError(null);
    try {
      const players = await TeamService.getBenchedPlayers(team.id);
      setBenchedPlayers(players);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch benched players');
    } finally {
      setLoading(false);
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
              <p className="text-slate-400">No team members found.</p>
            </div>
          ) : (
            <div className="overflow-y-auto max-h-[60vh]">
              <div className="grid gap-4">
                {benchedPlayers.map((player) => (
                  <div
                    key={player.id}
                    className="bg-slate-800 border border-slate-600 rounded-lg p-4"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-semibold text-white">
                        {player.username}
                      </span>
                      <span className={`text-sm ${getClassColor(player.class_)}`}>
                        {player.class_}
                      </span>
                      <span className="text-sm text-slate-400">
                        {player.role}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 text-sm text-slate-400">
            <p>
              <strong>Note:</strong> This shows all team members. In the future, this will show only players who are not assigned to current raids.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}; 