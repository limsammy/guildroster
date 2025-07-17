import React from 'react';
import { useGuild } from '../../contexts/GuildContext';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from './';

export const GuildSwitcher: React.FC = () => {
  const { user } = useAuth();
  const { selectedGuild, availableGuilds, isLoading, selectGuild } = useGuild();

  // Only show for superusers
  if (!user?.is_superuser) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-amber-500"></div>
        <span className="text-sm text-slate-300">Loading guilds...</span>
      </div>
    );
  }

  if (availableGuilds.length === 0) {
    return (
      <div className="flex items-center space-x-2">
        <span className="text-sm text-slate-400">No guilds available</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <span className="text-sm text-slate-300">Guild:</span>
      <div className="relative">
        <select
          value={selectedGuild?.id || ''}
          onChange={(e) => {
            const guildId = parseInt(e.target.value);
            const guild = availableGuilds.find(g => g.id === guildId) || null;
            selectGuild(guild);
          }}
          className="px-3 py-1.5 bg-slate-800 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
        >
          <option value="">All Guilds</option>
          {availableGuilds.map((guild) => (
            <option key={guild.id} value={guild.id}>
              {guild.name}
            </option>
          ))}
        </select>
      </div>
      {selectedGuild && (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => selectGuild(null)}
          className="text-xs px-2 py-1"
        >
          Clear
        </Button>
      )}
    </div>
  );
}; 