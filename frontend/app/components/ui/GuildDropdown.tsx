import React, { useState, useEffect } from 'react';
import { GuildService } from '../../api/guilds';
import type { Guild } from '../../api/types';

interface GuildDropdownProps {
  selectedGuildId: number | null;
  onGuildChange: (guildId: number | null) => void;
  className?: string;
}

export function GuildDropdown({ selectedGuildId, onGuildChange, className = '' }: GuildDropdownProps) {
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGuilds = async () => {
      try {
        setLoading(true);
        setError(null);
        const guildsData = await GuildService.getGuilds();
        setGuilds(guildsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load guilds');
      } finally {
        setLoading(false);
      }
    };

    fetchGuilds();
  }, []);

  if (loading) {
    return (
      <select 
        className={`w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-slate-400 ${className}`}
        disabled
      >
        <option>Loading guilds...</option>
      </select>
    );
  }

  if (error) {
    return (
      <select 
        className={`w-full px-3 py-2 bg-slate-800 border border-red-600 rounded-lg text-red-400 ${className}`}
        disabled
      >
        <option>Error loading guilds</option>
      </select>
    );
  }

  return (
    <select
      value={selectedGuildId || ''}
      onChange={(e) => onGuildChange(e.target.value ? Number(e.target.value) : null)}
      className={`w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent ${className}`}
    >
      <option value="">All Guilds</option>
      {guilds.map(guild => (
        <option key={guild.id} value={guild.id}>
          {guild.name}
        </option>
      ))}
    </select>
  );
} 