import React, { useState, useEffect } from 'react';
import { Link } from 'react-router';
import { Container, Button, Card } from '../components/ui';
import { ToonForm } from '../components/ui/ToonForm';
import { MemberSelector } from '../components/ui/MemberSelector';
import { ToonService, MemberService, TeamService } from '../api';
import type { Toon, ToonCreate, ToonUpdate, Member, Team } from '../api/types';

export default function Toons() {
  const [toons, setToons] = useState<Toon[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showMemberSelector, setShowMemberSelector] = useState(false);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);
  const [editingToon, setEditingToon] = useState<Toon | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [memberFilter, setMemberFilter] = useState<number | ''>('');

  useEffect(() => {
    loadToons();
    loadMembers();
    loadTeams();
  }, []);

  const loadToons = async () => {
    try {
      setLoading(true);
      const data = await ToonService.getToons();
      setToons(data);
      setError(null);
    } catch (err) {
      setError('Failed to load toons');
      console.error('Error loading toons:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMembers = async () => {
    try {
      const data = await MemberService.getMembers();
      setMembers(data);
    } catch (err) {
      console.error('Error loading members:', err);
    }
  };

  const loadTeams = async () => {
    try {
      const data = await TeamService.getTeams();
      setTeams(data);
    } catch (err) {
      console.error('Error loading teams:', err);
    }
  };

  // Add this function to reload toons from the API
  const reloadToons = async () => {
    const updatedToons = await ToonService.getToons();
    setToons(updatedToons);
  };

  const handleCreateToon = async (values: ToonCreate) => {
    try {
      setFormLoading(true);
      setFormError(null);
      await ToonService.createToon(values);
      await reloadToons();
      setShowForm(false);
      setSelectedMember(null);
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to create toon');
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateToon = async (values: ToonUpdate) => {
    if (!editingToon) return;
    try {
      setFormLoading(true);
      setFormError(null);
      await ToonService.updateToon(editingToon.id, values);
      await reloadToons();
      setEditingToon(null);
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to update toon');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteToon = async (toonId: number) => {
    if (!confirm('Are you sure you want to delete this toon?')) return;
    try {
      await ToonService.deleteToon(toonId);
      await reloadToons();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete toon');
    }
  };

  const handleEdit = (toon: Toon) => {
    setEditingToon(toon);
  };

  const handleCancel = () => {
    setShowForm(false);
    setShowMemberSelector(false);
    setSelectedMember(null);
    setEditingToon(null);
    setFormError(null);
  };

  const handleMemberSelect = (member: Member) => {
    setSelectedMember(member);
    setShowMemberSelector(false);
    setShowForm(true);
  };

  const handleStartCreateToon = () => {
    setShowMemberSelector(true);
  };

  const getMemberName = (memberId: number) => {
    const member = members.find(m => m.id === memberId);
    return member?.display_name || 'Unknown Member';
  };

  const filteredToons = toons.filter(toon => {
    const matchesSearch = toon.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         toon.class.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         toon.role.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMember = memberFilter === '' || toon.member_id === memberFilter;
    return matchesSearch && matchesMember;
  });

  if (showMemberSelector) {
    return (
      <MemberSelector
        onMemberSelect={handleMemberSelect}
        onCancel={handleCancel}
      />
    );
  }

  if (showForm || editingToon) {
    return (
      <Container>
        <div className="py-8">
          <ToonForm
            mode={editingToon ? 'edit' : 'add'}
            initialValues={editingToon || (selectedMember ? { member_id: selectedMember.id } : undefined)}
            members={editingToon ? members : (selectedMember ? [selectedMember] : members)}
            teams={teams}
            loading={formLoading}
            error={formError}
            onSubmit={editingToon ? handleUpdateToon : handleCreateToon}
            onCancel={handleCancel}
            hideMemberSelect={!editingToon && selectedMember !== null}
          />
        </div>
      </Container>
    );
  }

  return (
    <Container>
      <div className="py-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <nav className="flex items-center space-x-2 text-sm text-slate-400 mb-2">
              <Link to="/dashboard" className="hover:text-amber-400">
                Dashboard
              </Link>
              <span>/</span>
              <span className="text-slate-300">Toons</span>
            </nav>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
              Toons
            </h1>
            <p className="text-slate-300 mt-1">
              Manage character profiles and their assignments
            </p>
          </div>
          <div className="flex gap-3">
            <Link to="/dashboard">
              <Button variant="secondary">Back to Dashboard</Button>
            </Link>
            <Button onClick={handleStartCreateToon}>
              Add Toon
            </Button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-slate-800/60 border border-slate-600/50 rounded-lg p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name, class, or role..."
                className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Filter by Member
              </label>
              <select
                value={memberFilter}
                onChange={(e) => setMemberFilter(e.target.value ? Number(e.target.value) : '')}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              >
                <option value="">All Members</option>
                {members.map(member => (
                  <option key={member.id} value={member.id}>{member.display_name}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <Button
                variant="secondary"
                onClick={() => {
                  setSearchTerm('');
                  setMemberFilter('');
                }}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="text-slate-400 mb-4">
          {filteredToons.length} of {toons.length} toon{toons.length !== 1 ? 's' : ''}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-8">
            <div className="text-slate-400">Loading toons...</div>
          </div>
        )}

        {/* Toons List */}
        {!loading && (
          <div className="grid gap-4">
            {filteredToons.length === 0 ? (
              <Card variant="elevated" className="p-8 text-center">
                <p className="text-slate-400 mb-4">
                  {toons.length === 0 ? 'No toons found. Create your first toon!' : 'No toons match your search criteria.'}
                </p>
                {toons.length === 0 && (
                  <Button variant="primary" onClick={() => setShowForm(true)}>
                    Add First Toon
                  </Button>
                )}
              </Card>
            ) : (
              filteredToons.map(toon => (
                <Card key={toon.id} variant="elevated" className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-white">{toon.username}</h3>
                        {toon.is_main && (
                          <span className="bg-amber-500/20 text-amber-400 text-xs px-2 py-1 rounded-full">
                            Main
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-300">
                        <div>
                          <span className="text-slate-400">Class:</span> {toon.class}
                        </div>
                        <div>
                          <span className="text-slate-400">Role:</span> {toon.role}
                        </div>
                        <div>
                          <span className="text-slate-400">Member:</span> {getMemberName(toon.member_id)}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(toon)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteToon(toon.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}
      </div>
    </Container>
  );
} 