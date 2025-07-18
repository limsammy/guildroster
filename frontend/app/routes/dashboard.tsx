import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Button, Card, Container } from "../components/ui";
import { useAuth } from "../contexts/AuthContext";
import { useGuild } from "../contexts/GuildContext";
import { GuildService } from "../api/guilds";
import { TeamService } from "../api/teams";
import { MemberService } from "../api/members";
import { RaidService } from "../api/raids";
import { ScenarioService } from "../api/scenarios";
import type { Guild, Team, Member, Raid, Scenario } from "../api/types";

export function meta() {
  return [
    { title: "Dashboard - GuildRoster" },
    { name: "description", content: "Manage your guild's roster, teams, and raid attendance with GuildRoster dashboard." },
  ];
}

export default function Dashboard() {
  const { user } = useAuth();
  const { selectedGuild } = useGuild();
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [raids, setRaids] = useState<Raid[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all data in parallel
        const [guildsData, teamsData, membersData, raidsData, scenariosData] = await Promise.all([
          GuildService.getGuilds(),
          TeamService.getTeams(),
          MemberService.getMembers(),
          RaidService.getRaids(),
          ScenarioService.getScenarios(),
        ]);

        setGuilds(guildsData);
        setTeams(teamsData);
        setMembers(membersData);
        setRaids(raidsData);
        setScenarios(scenariosData);
      } catch (err: any) {
        console.error('Error fetching dashboard data:', err);
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Calculate statistics (filtered by selected guild if applicable)
  const filteredTeams = selectedGuild 
    ? teams.filter(team => team.guild_id === selectedGuild.id)
    : teams;
  const filteredMembers = selectedGuild
    ? members.filter(member => member.guild_id === selectedGuild.id)
    : members;
  const filteredRaids = selectedGuild
    ? raids.filter(raid => {
        const team = teams.find(t => t.id === raid.team_id);
        return team && team.guild_id === selectedGuild.id;
      })
    : raids;

  const totalTeams = filteredTeams.length;
  const totalMembers = filteredMembers.length;
  const totalRaids = filteredRaids.length;
  const activeScenarios = scenarios.filter(s => s.is_active).length;

  // Get recent raids (last 7 days, filtered by selected guild if applicable)
  const now = new Date();
  const lastWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const recentRaids = filteredRaids.filter(raid => {
    const raidDate = new Date(raid.scheduled_at);
    return raidDate >= lastWeek && raidDate <= now;
  }).sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime());

  // Group teams by guild (filtered by selected guild if applicable)
  const teamsByGuild = filteredTeams.reduce((acc, team) => {
    const guild = guilds.find(g => g.id === team.guild_id);
    const guildName = guild?.name || 'Unknown Guild';
    if (!acc[guildName]) {
      acc[guildName] = [];
    }
    acc[guildName].push(team);
    return acc;
  }, {} as Record<string, Team[]>);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Dashboard</h2>
          <p className="text-slate-300 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
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
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                  GuildRoster Dashboard
                </h1>
                <p className="text-slate-300 mt-1">
                  Welcome back, {user?.username || 'API User'}!
                </p>
                {selectedGuild && (
                  <p className="text-amber-400 text-sm mt-1">
                    Viewing: {selectedGuild.name}
                  </p>
                )}
              </div>
              <div className="flex gap-3">
                <Link to="/">
                  <Button variant="primary">Home</Button>
                </Link>
                <Link to="/login">
                  <Button variant="danger">Logout</Button>
                </Link>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-blue-400 mb-2">{totalTeams}</div>
              <div className="text-slate-300">
                {selectedGuild ? 'Teams' : 'Raid Teams'}
              </div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-green-400 mb-2">{totalMembers}</div>
              <div className="text-slate-300">
                {selectedGuild ? 'Members' : 'Members'}
              </div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-purple-400 mb-2">{totalRaids}</div>
              <div className="text-slate-300">
                {selectedGuild ? 'Raids' : 'Total Raids'}
              </div>
            </Card>
            <Card variant="elevated" className="text-center p-6">
              <div className="text-3xl font-bold text-orange-400 mb-2">{activeScenarios}</div>
              <div className="text-slate-300">Active Scenarios</div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upcoming Raids */}
            <Card variant="elevated" className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Recent Raids</h2>
                <Button size="sm" variant="primary">
                  View All
                </Button>
              </div>
              
              {recentRaids.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">📅</div>
                  <p className="text-slate-300">No recent raids scheduled</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {recentRaids.slice(0, 5).map((raid) => {
                    const team = teams.find(t => t.id === raid.team_id);
                    const scenario = scenarios.find(s => s.id === raid.scenario_id);
                    const raidDate = new Date(raid.scheduled_at);
                    
                    return (
                      <div key={raid.id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-600/30">
                        <div>
                          <div className="font-semibold text-white">
                            {scenario?.name || 'Unknown Scenario'}
                          </div>
                          <div className="text-sm text-slate-300">
                            {team?.name || 'Unknown Team'} • {scenario?.difficulty || 'Unknown'} • {scenario?.size || 'Unknown'}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-amber-400">
                            {raidDate.toLocaleDateString()}
                          </div>
                          <div className="text-xs text-slate-400">
                            {raidDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>

            {/* Quick Actions */}
            <Card variant="elevated" className="p-6">
              <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-4">
                <Link to="/raids" className="block">
                  <Button className="w-full h-20 flex flex-col items-center justify-center" variant="primary">
                    <div className="text-3xl mb-2">➕</div>
                    <div className="text-sm font-medium">Add Raid</div>
                  </Button>
                </Link>
                <Link to="/raids" className="block">
                  <Button className="w-full h-20 flex flex-col items-center justify-center" variant="primary">
                    <div className="text-3xl mb-2">🗡️</div>
                    <div className="text-sm font-medium">Manage Raids</div>
                  </Button>
                </Link>
                <Link to="/teams" className="block">
                  <Button className="w-full h-20 flex flex-col items-center justify-center" variant="primary">
                    <div className="text-3xl mb-2">👥</div>
                    <div className="text-sm font-medium">Manage Teams</div>
                  </Button>
                </Link>
                <Link to="/members" className="block">
                  <Button className="w-full h-20 flex flex-col items-center justify-center" variant="primary">
                    <div className="text-3xl mb-2">🧑‍🤝‍🧑</div>
                    <div className="text-sm font-medium">Manage Members</div>
                  </Button>
                </Link>
                <Link to="/toons" className="block">
                  <Button className="w-full h-20 flex flex-col items-center justify-center" variant="primary">
                    <div className="text-3xl mb-2">⚔️</div>
                    <div className="text-sm font-medium">Manage Toons</div>
                  </Button>
                </Link>
                {user?.is_superuser && (
                  <Link to="/settings" className="block">
                    <Button className="w-full h-20 flex flex-col items-center justify-center" variant="primary">
                      <div className="text-3xl mb-2">⚙️</div>
                      <div className="text-sm font-medium">Settings</div>
                    </Button>
                  </Link>
                )}
              </div>
            </Card>
          </div>

          {/* Raid Teams by Guild */}
          <div className="mt-8">
            <Card variant="elevated" className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">
                  {selectedGuild ? `${selectedGuild.name} Teams` : 'Raid Teams'}
                </h2>
                <Link to="/teams">
                  <Button size="sm" variant="primary">
                    Manage Teams
                  </Button>
                </Link>
              </div>

              {Object.keys(teamsByGuild).length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">🏰</div>
                  <p className="text-slate-300">
                    {selectedGuild ? `No teams found in ${selectedGuild.name}` : 'No raid teams found'}
                  </p>
                  <p className="text-slate-400 text-sm mt-2">Create your first team to get started</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {Object.entries(teamsByGuild).map(([guildName, guildTeams]) => (
                    <div key={guildName} className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4">
                      {!selectedGuild && (
                        <h3 className="font-semibold text-white mb-3">{guildName}</h3>
                      )}
                      <div className="space-y-2">
                        {guildTeams.map((team) => {
                          const teamMembers = filteredMembers.filter(m => m.team_id === team.id);
                          const teamRaids = filteredRaids.filter(r => r.team_id === team.id);
                          
                          return (
                            <div key={team.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded border border-slate-600/20">
                              <div>
                                <div className="font-medium text-amber-400">{team.name}</div>
                                <div className="text-sm text-slate-300">
                                  {teamMembers.length} members • {teamRaids.length} raids
                                </div>
                              </div>
                              <Button size="sm" variant="ghost">
                                View
                              </Button>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>
      </Container>
    </div>
  );
} 