import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { GuildService } from '../api/guilds';
import { useAuth } from './AuthContext';
import type { Guild } from '../api/types';

interface GuildContextType {
  selectedGuild: Guild | null;
  availableGuilds: Guild[];
  isLoading: boolean;
  error: string | null;
  selectGuild: (guild: Guild | null) => void;
  refreshGuilds: () => Promise<void>;
  clearError: () => void;
}

const GuildContext = createContext<GuildContextType | undefined>(undefined);

interface GuildProviderProps {
  children: ReactNode;
}

export const GuildProvider: React.FC<GuildProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const [selectedGuild, setSelectedGuild] = useState<Guild | null>(null);
  const [availableGuilds, setAvailableGuilds] = useState<Guild[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available guilds on mount and when user changes
  useEffect(() => {
    if (user?.is_superuser) {
      loadGuilds();
    } else {
      // For non-superusers, clear guild context
      setAvailableGuilds([]);
      setSelectedGuild(null);
    }
  }, [user]);

  // Load selected guild from localStorage on mount
  useEffect(() => {
    if (user?.is_superuser) {
      const savedGuildId = localStorage.getItem('selectedGuildId');
      if (savedGuildId && availableGuilds.length > 0) {
        const guild = availableGuilds.find(g => g.id === parseInt(savedGuildId));
        if (guild) {
          setSelectedGuild(guild);
        }
      }
    }
  }, [availableGuilds, user]);

  const loadGuilds = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const guilds = await GuildService.getGuilds();
      setAvailableGuilds(guilds);
    } catch (err: any) {
      setError(err.message || 'Failed to load guilds');
      console.error('Error loading guilds:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const selectGuild = (guild: Guild | null) => {
    setSelectedGuild(guild);
    if (guild) {
      localStorage.setItem('selectedGuildId', guild.id.toString());
    } else {
      localStorage.removeItem('selectedGuildId');
    }
  };

  const refreshGuilds = async () => {
    await loadGuilds();
  };

  const clearError = () => {
    setError(null);
  };

  const value: GuildContextType = {
    selectedGuild,
    availableGuilds,
    isLoading,
    error,
    selectGuild,
    refreshGuilds,
    clearError,
  };

  return (
    <GuildContext.Provider value={value}>
      {children}
    </GuildContext.Provider>
  );
};

export const useGuild = (): GuildContextType => {
  const context = useContext(GuildContext);
  if (context === undefined) {
    throw new Error('useGuild must be used within a GuildProvider');
  }
  return context;
}; 