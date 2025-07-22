import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { AttendanceService } from '../api/attendance';
import { RaidService } from '../api/raids';
import { ToonService } from '../api/toons';
import { TeamService } from '../api/teams';
import type { Attendance, Raid, Toon, Team } from '../api/types';
import { AttendanceForm } from '../components/ui/AttendanceForm';

export function meta() {
  return [
    { title: 'Attendance - GuildRoster' },
    { name: 'description', content: 'Track raid attendance and participation.' },
  ];
}

export default function Attendance() {
  const { user } = useAuth();
  const [attendance, setAttendance] = useState<Attendance[]>([]);
  const [raids, setRaids] = useState<Raid[]>([]);
  const [toons, setToons] = useState<Toon[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [teamFilter, setTeamFilter] = useState<number | ''>('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'present' | 'absent'>('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAttendance, setEditingAttendance] = useState<Attendance | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [attendanceData, raidsData, toonsData, teamsData] = await Promise.all([
          AttendanceService.getAttendance(),
          RaidService.getRaids(),
          ToonService.getToons(),
          TeamService.getTeams(),
        ]);
        setAttendance(attendanceData);
        setRaids(raidsData);
        setToons(toonsData);
        setTeams(teamsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Helper function to get raid info by ID
  const getRaidInfo = (raidId: number) => {
    const raid = raids.find(r => r.id === raidId);
    return raid ? {
      id: raid.id,
      scheduled_at: raid.scheduled_at,
      team_id: raid.team_id,
      scenario_id: raid.scenario_id,
    } : null;
  };

  // Helper function to get toon info by ID
  const getToonInfo = (toonId: number) => {
    const toon = toons.find(t => t.id === toonId);
    return toon ? {
      id: toon.id,
      username: toon.username,
      class: toon.class,
      role: toon.role,
      
    } : null;
  };

  // Helper function to get team name by ID
  const getTeamName = (teamId: number) => {
    const team = teams.find(t => t.id === teamId);
    return team ? team.name : `Team #${teamId}`;
  };

  // Helper function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Reload attendance from the API
  const reloadAttendance = async () => {
    try {
      const updatedAttendance = await AttendanceService.getAttendance();
      setAttendance(updatedAttendance);
    } catch (err: any) {
      setError(err.message || 'Failed to reload attendance');
    }
  };

  // Fetch data when showing the form
  const openAddForm = async () => {
    setFormLoading(true);
    setFormError(null);
    try {
      const [raidsData, toonsData] = await Promise.all([
        RaidService.getRaids(),
        ToonService.getToons(),
      ]);
      setRaids(raidsData);
      setToons(toonsData);
      setShowAddForm(true);
    } catch (err: any) {
      setFormError(err.message || 'Failed to load form data');
    } finally {
      setFormLoading(false);
    }
  };

  const openEditForm = async (attendanceRecord: Attendance) => {
    setFormLoading(true);
    setFormError(null);
    try {
      const [raidsData, toonsData] = await Promise.all([
        RaidService.getRaids(),
        ToonService.getToons(),
      ]);
      setRaids(raidsData);
      setToons(toonsData);
      setEditingAttendance(attendanceRecord);
    } catch (err: any) {
      setFormError(err.message || 'Failed to load form data');
    } finally {
      setFormLoading(false);
    }
  };

  const handleAddAttendance = async (values: { raid_id: number; toon_id: number; is_present: boolean; notes?: string }) => {
    setFormLoading(true);
    setFormError(null);
    try {
      await AttendanceService.createAttendance({
        raid_id: values.raid_id,
        toon_id: values.toon_id,
        is_present: values.is_present,
        notes: values.notes || undefined,
      });
      setShowAddForm(false);
      await reloadAttendance();
    } catch (err: any) {
      setFormError(err.message || 'Failed to add attendance record');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditAttendance = async (values: { raid_id: number; toon_id: number; is_present: boolean; notes?: string }) => {
    if (!editingAttendance) return;
    setFormLoading(true);
    setFormError(null);
    try {
      await AttendanceService.updateAttendance(editingAttendance.id, {
        raid_id: values.raid_id,
        toon_id: values.toon_id,
        is_present: values.is_present,
        notes: values.notes || undefined,
      });
      setEditingAttendance(null);
      await reloadAttendance();
    } catch (err: any) {
      setFormError(err.message || 'Failed to update attendance record');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteAttendance = async (attendanceId: number) => {
    if (!confirm('Are you sure you want to delete this attendance record? This action cannot be undone.')) return;
    try {
      await AttendanceService.deleteAttendance(attendanceId);
      await reloadAttendance();
    } catch (err: any) {
      setError(err.message || 'Failed to delete attendance record');
    }
  };

  const handleCancelForm = () => {
    setShowAddForm(false);
    setEditingAttendance(null);
    setFormError(null);
  };

  // Filter attendance based on search and filters
  const filteredAttendance = attendance.filter(record => {
    const raidInfo = getRaidInfo(record.raid_id);
    const toonInfo = getToonInfo(record.toon_id);
    
    if (!raidInfo || !toonInfo) return false;

    const matchesSearch = searchTerm === '' || 
      record.id.toString().includes(searchTerm) ||
      toonInfo.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      toonInfo.class.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDate = dateFilter === '' || 
      raidInfo.scheduled_at.startsWith(dateFilter);
    
    const matchesTeam = teamFilter === '' || 
      raidInfo.team_id === teamFilter;
    
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'present' && record.is_present) ||
      (statusFilter === 'absent' && !record.is_present);
    
    return matchesSearch && matchesDate && matchesTeam && matchesStatus;
  });

  // Sort attendance by raid date (newest first)
  const sortedAttendance = [...filteredAttendance].sort((a, b) => {
    const raidA = getRaidInfo(a.raid_id);
    const raidB = getRaidInfo(b.raid_id);
    if (!raidA || !raidB) return 0;
    return new Date(raidB.scheduled_at).getTime() - new Date(raidA.scheduled_at).getTime();
  });

  // Calculate quick statistics
  const totalRecords = attendance.length;
  const presentRecords = attendance.filter(r => r.is_present).length;
  const attendanceRate = totalRecords > 0 ? Math.round((presentRecords / totalRecords) * 100) : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading attendance...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Attendance</h2>
          <p className="text-slate-300 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-slate-800/60 border-b border-slate-600/50">
        <Container>
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <nav className="flex items-center space-x-2 text-sm text-slate-400 mb-2">
                  <Link to="/dashboard" className="hover:text-amber-400">Dashboard</Link>
                  <span>/</span>
                  <span className="text-slate-300">Attendance</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Attendance</h1>
                <p className="text-slate-300 mt-1">Track raid attendance and participation</p>
              </div>
              <div className="flex gap-3">
                <Link to="/dashboard">
                  <Button variant="secondary">Dashboard</Button>
                </Link>
                <Button variant="primary" onClick={openAddForm}>
                  Add Record
                </Button>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Quick Statistics */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-white">{totalRecords}</div>
                <div className="text-slate-400 text-sm">Total Records</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-400">{presentRecords}</div>
                <div className="text-slate-400 text-sm">Present</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-amber-400">{attendanceRate}%</div>
                <div className="text-slate-400 text-sm">Attendance Rate</div>
              </div>
            </div>
          </Card>

          {/* Search and Filter Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <label htmlFor="search" className="block text-sm font-medium text-slate-300 mb-2">
                  Search
                </label>
                <input
                  id="search"
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder="Search by ID, toon, or class..."
                />
              </div>
              <div>
                <label htmlFor="date-filter" className="block text-sm font-medium text-slate-300 mb-2">
                  Date
                </label>
                <input
                  id="date-filter"
                  type="date"
                  value={dateFilter}
                  onChange={e => setDateFilter(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="team-filter" className="block text-sm font-medium text-slate-300 mb-2">
                  Team
                </label>
                <select
                  id="team-filter"
                  value={teamFilter}
                  onChange={e => setTeamFilter(e.target.value ? Number(e.target.value) : '')}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  <option value="">All Teams</option>
                  {teams.map(team => (
                    <option key={team.id} value={team.id}>{team.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="status-filter" className="block text-sm font-medium text-slate-300 mb-2">
                  Status
                </label>
                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={e => setStatusFilter(e.target.value as 'all' | 'present' | 'absent')}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  <option value="all">All</option>
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                </select>
              </div>
              <div className="flex items-end">
                <Button 
                  variant="secondary" 
                  onClick={() => {
                    setSearchTerm('');
                    setDateFilter('');
                    setTeamFilter('');
                    setStatusFilter('all');
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </Card>

          {/* Attendance List */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Attendance Records</h2>
              <div className="text-sm text-slate-400">
                {sortedAttendance.length} of {attendance.length} records
              </div>
            </div>

            {sortedAttendance.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-slate-400 text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {searchTerm || dateFilter || teamFilter !== '' || statusFilter !== 'all' ? 'No records found' : 'No attendance records yet'}
                </h3>
                <p className="text-slate-400 mb-6">
                  {searchTerm || dateFilter || teamFilter !== '' || statusFilter !== 'all' 
                    ? 'Try adjusting your search terms or filters' 
                    : 'Get started by adding your first attendance record'
                  }
                </p>
                {!searchTerm && !dateFilter && teamFilter === '' && statusFilter === 'all' && (
                  <Button variant="primary" onClick={openAddForm}>
                    Add First Record
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {sortedAttendance.map(record => {
                  const raidInfo = getRaidInfo(record.raid_id);
                  const toonInfo = getToonInfo(record.toon_id);
                  
                  if (!raidInfo || !toonInfo) return null;

                  return (
                    <div
                      key={record.id}
                      className={`flex items-center justify-between p-4 rounded-lg border transition-colors ${
                        record.is_present
                          ? 'bg-slate-800/50 border-green-600/30'
                          : 'bg-slate-800/30 border-red-600/30'
                      }`}
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-4 mb-2">
                          <span className="text-white font-medium">Record #{record.id}</span>
                          <span className={`px-2 py-1 text-xs rounded ${
                            record.is_present 
                              ? 'bg-green-600/20 text-green-400' 
                              : 'bg-red-600/20 text-red-400'
                          }`}>
                            {record.is_present ? 'Present' : 'Absent'}
                          </span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-slate-400">
                          <div>
                            <span className="font-medium text-slate-300">Raid:</span>
                            <br />
                            Raid #{raidInfo.id} - {formatDate(raidInfo.scheduled_at)}
                          </div>
                          <div>
                            <span className="font-medium text-slate-300">Toon:</span>
                            <br />
                            {toonInfo.username} ({toonInfo.class} - {toonInfo.role})
                          </div>
                          <div>
                            <span className="font-medium text-slate-300">Team:</span>
                            <br />
                            {getTeamName(raidInfo.team_id)}
                          </div>
                          <div>
                            <span className="font-medium text-slate-300">Notes:</span>
                            <br />
                            {record.notes || 'No notes'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => openEditForm(record)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleDeleteAttendance(record.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>
      </Container>

      {/* Add/Edit Form Modal */}
      {(showAddForm || editingAttendance) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md">
            <AttendanceForm
              raids={raids}
              toons={toons}
              loading={formLoading}
              error={formError}
              onSubmit={showAddForm ? handleAddAttendance : handleEditAttendance}
              onCancel={handleCancelForm}
              isEditing={!!editingAttendance}
              initialValues={editingAttendance ? {
                raid_id: editingAttendance.raid_id,
                toon_id: editingAttendance.toon_id,
                is_present: editingAttendance.is_present,
                notes: editingAttendance.notes || '',
              } : {}}
            />
          </div>
        </div>
      )}
    </div>
  );
} 