import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { AttendanceService } from '../../api/attendance';
import { Card } from './index';
import { GuildDropdown } from './GuildDropdown';
import { TeamDropdown } from './TeamDropdown';
import { RaidCountSelector } from './RaidCountSelector';
import { AttendanceTable } from './AttendanceTable';
import type { TeamViewData } from '../../api/types';

interface AttendanceTeamViewProps {
  className?: string;
}

export function AttendanceTeamView({ className = '' }: AttendanceTeamViewProps) {
  const { user } = useAuth();
  const [selectedGuildId, setSelectedGuildId] = useState<number | null>(null);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [raidCount, setRaidCount] = useState(5);
  const [data, setData] = useState<TeamViewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [exportPeriod, setExportPeriod] = useState<'current' | 'all' | 'custom'>('current');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [exportEnabled, setExportEnabled] = useState(false);

  // Check if export is enabled on component mount
  useEffect(() => {
    const checkExportStatus = async () => {
      try {
        const enabled = await AttendanceService.isExportEnabled();
        setExportEnabled(enabled);
      } catch (error) {
        console.error('Failed to check export status:', error);
        setExportEnabled(false);
      }
    };
    
    checkExportStatus();
  }, []);

  // Reset team selection when guild changes
  useEffect(() => {
    setSelectedTeamId(null);
    setData(null);
  }, [selectedGuildId]);

  // Fetch team view data when team or raid count changes
  useEffect(() => {
    const fetchTeamView = async () => {
      if (!selectedTeamId) {
        setData(null);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const teamViewData = await AttendanceService.getTeamAttendanceView(
          selectedTeamId,
          raidCount,
          selectedGuildId || undefined
        );
        setData(teamViewData);
      } catch (err: any) {
        setError(err.message || 'Failed to load team attendance data');
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamView();
  }, [selectedTeamId, raidCount, selectedGuildId]);

  const handleGuildChange = (guildId: number | null) => {
    setSelectedGuildId(guildId);
  };

  const handleTeamChange = (teamId: number | null) => {
    setSelectedTeamId(teamId);
  };

  const handleRaidCountChange = (count: number) => {
    setRaidCount(count);
  };

  const handleExportTeam = async () => {
    if (!selectedTeamId) return;

    try {
      setExportLoading(true);
      
      let startDate: string | undefined;
      let endDate: string | undefined;
      
      if (exportPeriod === 'custom') {
        if (!customStartDate || !customEndDate) {
          alert('Please select both start and end dates for custom period');
          return;
        }
        startDate = customStartDate;
        endDate = customEndDate;
      }
      
      const blob = await AttendanceService.exportTeamImage(
        selectedTeamId,
        exportPeriod,
        startDate,
        endDate,
        20 // Use more raids for export
      );
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `team_attendance_${selectedTeamId}_${new Date().toISOString().split('T')[0]}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (err: any) {
      alert(`Export failed: ${err.message || 'Unknown error'}`);
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportAllTeams = async () => {
    try {
      setExportLoading(true);
      
      let startDate: string | undefined;
      let endDate: string | undefined;
      
      if (exportPeriod === 'custom') {
        if (!customStartDate || !customEndDate) {
          alert('Please select both start and end dates for custom period');
          return;
        }
        startDate = customStartDate;
        endDate = customEndDate;
      }
      
      const blob = await AttendanceService.exportAllTeamsImages(
        selectedGuildId || undefined,
        exportPeriod,
        startDate,
        endDate,
        20 // Use more raids for export
      );
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `all_teams_attendance_${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (err: any) {
      alert(`Export failed: ${err.message || 'Unknown error'}`);
    } finally {
      setExportLoading(false);
    }
  };

  return (
    <div className={className}>
      {/* Controls */}
      <Card variant="elevated" className="p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Guild Dropdown (Superusers only) */}
          {user?.is_superuser && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Guild
              </label>
              <GuildDropdown
                selectedGuildId={selectedGuildId}
                onGuildChange={handleGuildChange}
              />
            </div>
          )}
          
          {/* Team Dropdown */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Team
            </label>
            <TeamDropdown
              selectedTeamId={selectedTeamId}
              onTeamChange={handleTeamChange}
              guildId={selectedGuildId}
            />
          </div>
          
          {/* Raid Count Selector */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Time Period
            </label>
            <RaidCountSelector
              raidCount={raidCount}
              onRaidCountChange={handleRaidCountChange}
            />
          </div>
          
          {/* Clear Selection */}
          <div className="flex items-end">
            <button
              onClick={() => {
                setSelectedGuildId(null);
                setSelectedTeamId(null);
                setData(null);
              }}
              className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Clear Selection
            </button>
          </div>
        </div>
      </Card>

      {/* Export Controls */}
      {(selectedTeamId || selectedGuildId) && (
        <Card variant="elevated" className="p-6 mb-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white mb-2">Export Reports</h3>
            <p className="text-sm text-slate-400">
              Generate attendance report images for sharing in Discord
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* Export Period */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Export Period
              </label>
              <select
                value={exportPeriod}
                onChange={(e) => setExportPeriod(e.target.value as 'current' | 'all' | 'custom')}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              >
                <option value="current">Current Week</option>
                <option value="all">All Time</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
            
            {/* Custom Date Range */}
            {exportPeriod === 'custom' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={customStartDate}
                    onChange={(e) => setCustomStartDate(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={customEndDate}
                    onChange={(e) => setCustomEndDate(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  />
                </div>
              </>
            )}
          </div>
          
          <div className="flex gap-3">
            {selectedTeamId && (
              <button
                onClick={handleExportTeam}
                disabled={exportLoading}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:bg-slate-600 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                {exportLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Exporting...
                  </>
                ) : (
                  <>
                    📊 Export Team Report
                  </>
                )}
              </button>
            )}
            
            {exportEnabled && (
              <button
                onClick={handleExportAllTeams}
                disabled={exportLoading}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                {exportLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Exporting...
                  </>
                ) : (
                  <>
                    📦 Export All Teams (ZIP)
                  </>
                )}
              </button>
            )}
          </div>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <Card variant="elevated" className="p-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
            <p className="text-slate-300">Loading team attendance data...</p>
          </div>
        </Card>
      )}

      {/* Error State */}
      {error && !loading && (
        <Card variant="elevated" className="p-12">
          <div className="text-center">
            <div className="text-red-400 text-6xl mb-4">⚠️</div>
            <h3 className="text-xl font-semibold text-white mb-2">Error Loading Data</h3>
            <p className="text-slate-300 mb-4">{error}</p>
            <button
              onClick={() => {
                setError(null);
                if (selectedTeamId) {
                  // Retry loading
                  setSelectedTeamId(null);
                  setTimeout(() => setSelectedTeamId(selectedTeamId), 100);
                }
              }}
              className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </Card>
      )}

      {/* No Team Selected */}
      {!selectedTeamId && !loading && !error && (
        <Card variant="elevated" className="p-12">
          <div className="text-center">
            <div className="text-slate-400 text-6xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-white mb-2">Select a Team</h3>
            <p className="text-slate-300">
              Choose a team from the dropdown above to view attendance data.
            </p>
          </div>
        </Card>
      )}

      {/* Team View Data */}
      {data && !loading && !error && (
        <Card variant="elevated" className="p-6">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">
              {data.team.name} - Attendance Overview
            </h2>
            <p className="text-slate-300">
              Showing attendance for the last {raidCount} raids
              {data.toons.length > 0 && (
                <span> • {data.toons.length} toons • {data.raids.length} raids</span>
              )}
            </p>
          </div>
          
          <AttendanceTable data={data} />
        </Card>
      )}
    </div>
  );
} 