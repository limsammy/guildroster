import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { AttendanceService } from '../api/attendance';
import { RaidService } from '../api/raids';
import { ToonService } from '../api/toons';
import { TeamService } from '../api/teams';
import type { Attendance, Raid, Toon, Team, AttendanceStatus } from '../api/types';
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
  const [statusFilter, setStatusFilter] = useState<'all' | AttendanceStatus>('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAttendance, setEditingAttendance] = useState<Attendance | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [raidFilter, setRaidFilter] = useState<number[]>([]);
  const [raidFilterExpanded, setRaidFilterExpanded] = useState(false);

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
      // scenario_id: raid.scenario_id, // Remove this line, not present in Raid type
      // Optionally add scenario_name, scenario_difficulty, scenario_size if needed
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

  const handleAddAttendance = async (values: { raid_id: number; toon_id: number; status: AttendanceStatus; notes?: string; benched_note?: string }) => {
    setFormLoading(true);
    setFormError(null);
    try {
      await AttendanceService.createAttendance({
        raid_id: values.raid_id,
        toon_id: values.toon_id,
        status: values.status,
        notes: values.notes || undefined,
        benched_note: values.benched_note || undefined,
      });
      setShowAddForm(false);
      await reloadAttendance();
    } catch (err: any) {
      setFormError(err.message || 'Failed to add attendance record');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditAttendance = async (values: { raid_id: number; toon_id: number; status: AttendanceStatus; notes?: string; benched_note?: string }) => {
    if (!editingAttendance) return;
    setFormLoading(true);
    setFormError(null);
    try {
      await AttendanceService.updateAttendance(editingAttendance.id, {
        raid_id: values.raid_id,
        toon_id: values.toon_id,
        status: values.status,
        notes: values.notes || undefined,
        benched_note: values.benched_note || undefined,
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
      record.status === statusFilter;

    const matchesRaid = raidFilter.length === 0 || raidFilter.includes(record.raid_id);
    
    return matchesSearch && matchesDate && matchesTeam && matchesStatus && matchesRaid;
  });

  // Sort attendance by raid date (newest first)
  const sortedAttendance = [...filteredAttendance].sort((a, b) => {
    const raidA = getRaidInfo(a.raid_id);
    const raidB = getRaidInfo(b.raid_id);
    if (!raidA || !raidB) return 0;
    return new Date(raidB.scheduled_at).getTime() - new Date(raidA.scheduled_at).getTime();
  });

  // Group attendance records by raid
  const attendanceByRaid: Record<number, Attendance[]> = {};
  sortedAttendance.forEach(record => {
    if (!attendanceByRaid[record.raid_id]) attendanceByRaid[record.raid_id] = [];
    attendanceByRaid[record.raid_id].push(record);
  });

  // Calculate quick statistics
  const totalRecords = attendance.length;
  const presentRecords = attendance.filter(r => r.status === 'present').length;
  const benchedRecords = attendance.filter(r => r.status === 'benched').length;
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
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-white">{totalRecords}</div>
                <div className="text-slate-400 text-sm">Total Records</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-400">{presentRecords}</div>
                <div className="text-slate-400 text-sm">Present</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-400">{benchedRecords}</div>
                <div className="text-slate-400 text-sm">Benched</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-amber-400">{attendanceRate}%</div>
                <div className="text-slate-400 text-sm">Attendance Rate</div>
              </div>
            </div>
          </Card>

          {/* Search and Filter Controls */}
          <Card variant="elevated" className="p-6 mb-6">
            <div className="hidden md:grid md:grid-cols-7 gap-4 mb-1">
              <div><label htmlFor="search" className="block text-sm font-medium text-slate-300">Search</label></div>
              <div><label htmlFor="date-filter" className="block text-sm font-medium text-slate-300">Date</label></div>
              <div><label htmlFor="team-filter" className="block text-sm font-medium text-slate-300">Team</label></div>
              <div><label htmlFor="status-filter" className="block text-sm font-medium text-slate-300">Status</label></div>
              <div className="col-span-2"><label htmlFor="raid-filter" className="block text-sm font-medium text-slate-300">Raids</label></div>
              <div></div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-7 gap-4 items-start">
              <div className="flex flex-col">
                <input
                  id="search"
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 min-h-[40px] bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder="Search by ID, toon, or class..."
                />
              </div>
              <div className="flex flex-col">
                <input
                  id="date-filter"
                  type="date"
                  value={dateFilter}
                  onChange={e => setDateFilter(e.target.value)}
                  className="w-full px-2 py-2 min-h-[40px] bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
              </div>
              <div className="flex flex-col">
                <select
                  id="team-filter"
                  value={teamFilter}
                  onChange={e => setTeamFilter(e.target.value ? Number(e.target.value) : '')}
                  className="w-full px-2 py-2 min-h-[40px] bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  <option value="">All Teams</option>
                  {teams.map(team => (
                    <option key={team.id} value={team.id}>{team.name}</option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col">
                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={e => setStatusFilter(e.target.value as 'all' | AttendanceStatus)}
                  className="w-full px-2 py-2 min-h-[40px] bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  <option value="all">All</option>
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                  <option value="benched">Benched</option>
                </select>
              </div>
              <div className="col-span-2 flex flex-col">
                <div className="flex flex-row gap-2">
                  <select
                    id="raid-filter"
                    multiple
                    value={raidFilter.map(String)}
                    onChange={e => {
                      const selected = Array.from(e.target.selectedOptions, option => Number(option.value));
                      setRaidFilter(selected);
                    }}
                    className={`w-full px-3 py-2 min-h-[40px] bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-200 ${raidFilterExpanded ? 'h-32' : 'h-10'} ${raidFilterExpanded ? 'whitespace-normal' : 'overflow-hidden whitespace-nowrap text-ellipsis'}`}
                    style={raidFilterExpanded ? {} : { minHeight: '2.5rem' }}
                  >
                    {raids.map(raid => (
                      <option key={raid.id} value={raid.id}
                        className={raidFilterExpanded ? '' : 'truncate'}
                        style={raidFilterExpanded ? {} : { maxWidth: '100%' }}
                      >
                        Raid #{raid.id} - {new Date(raid.scheduled_at).toLocaleString()} ({raid.scenario_name})
                      </option>
                    ))}
                  </select>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    className="shrink-0 min-h-[40px] ml-2"
                    onClick={() => setRaidFilterExpanded(expanded => !expanded)}
                    aria-label={raidFilterExpanded ? 'Collapse raid filter' : 'Expand raid filter'}
                  >
                    {raidFilterExpanded ? 'Collapse' : 'Expand'}
                  </Button>
                </div>
                <div className="text-xs text-slate-400 mt-1 text-left">
                  Hold Ctrl/Cmd to select multiple
                </div>
              </div>
              <div className="flex items-center h-full">
                <Button 
                  variant="danger" 
                  size="sm"
                  onClick={() => {
                    setSearchTerm('');
                    setDateFilter('');
                    setTeamFilter('');
                    setStatusFilter('all');
                    setRaidFilter([]);
                  }}
                  className="w-full px-2 py-1 text-xs min-h-[40px]"
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
                  {searchTerm || dateFilter || teamFilter !== '' || statusFilter !== 'all' || raidFilter.length > 0 ? 'No records found' : 'No attendance records yet'}
                </h3>
                <p className="text-slate-400 mb-6">
                  {searchTerm || dateFilter || teamFilter !== '' || statusFilter !== 'all' || raidFilter.length > 0 
                    ? 'Try adjusting your search terms or filters' 
                    : 'Get started by adding your first attendance record'
                  }
                </p>
                {!searchTerm && !dateFilter && teamFilter === '' && statusFilter === 'all' && raidFilter.length === 0 && (
                  <Button variant="primary" onClick={openAddForm}>
                    Add First Record
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-8">
                {Object.entries(attendanceByRaid).map(([raidId, records]) => {
                  const raidInfo = getRaidInfo(Number(raidId));
                  return (
                    <Card key={raidId} variant="bordered" className="p-4">
                      <div className="mb-4 flex flex-col md:flex-row md:items-center md:justify-between">
                        <div className="font-semibold text-lg text-amber-400">
                          Raid #{raidInfo?.id} - {raidInfo ? formatDate(raidInfo.scheduled_at) : ''}
                        </div>
                        <div className="text-sm text-slate-400 mt-1 md:mt-0">
                          Team: {getTeamName(raidInfo?.team_id ?? 0)}
                        </div>
                      </div>
                      <div className="space-y-4">
                        {records.map(record => {
                          const toonInfo = getToonInfo(record.toon_id);
                          if (!raidInfo || !toonInfo) return null;
                          return (
                            <div
                              key={record.id}
                              className={`flex items-center justify-between p-4 rounded-lg border transition-colors ${
                                record.status === 'present'
                                  ? 'bg-slate-800/50 border-green-600/30'
                                  : record.status === 'benched'
                                  ? 'bg-slate-800/40 border-yellow-600/30'
                                  : 'bg-slate-800/30 border-red-600/30'
                              }`}
                            >
                              <div className="flex-1">
                                <div className="flex items-center space-x-4 mb-2">
                                  <span className="text-white font-medium">Record #{record.id}</span>
                                  <span className={`px-2 py-1 text-xs rounded ${
                                    record.status === 'present'
                                      ? 'bg-green-600/20 text-green-400' 
                                      : record.status === 'benched'
                                      ? 'bg-yellow-600/20 text-yellow-400'
                                      : 'bg-red-600/20 text-red-400'
                                  }`}>
                                    {record.status === 'present' ? 'Present' : record.status === 'benched' ? 'Benched' : 'Absent'}
                                  </span>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-400">
                                  <div>
                                    <span className="font-medium text-slate-300">Toon:</span>
                                    <br />
                                    {toonInfo.username} ({toonInfo.class} - {toonInfo.role})
                                  </div>
                                  <div>
                                    <span className="font-medium text-slate-300">Notes:</span>
                                    <br />
                                    {record.notes || 'No notes'}
                                  </div>
                                  {record.status === 'benched' && record.benched_note && (
                                    <div>
                                      <span className="font-medium text-yellow-300">Benched Note:</span>
                                      <br />
                                      {record.benched_note}
                                    </div>
                                  )}
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
                    </Card>
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
                status: editingAttendance.status,
                notes: editingAttendance.notes || '',
                benched_note: editingAttendance.benched_note || '',
              } : {}}
            />
          </div>
        </div>
      )}
    </div>
  );
} 