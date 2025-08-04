import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { InviteService } from '../api/invites';
import { AuthService } from '../api/auth';
import type { Invite } from '../api/types';
import type { UserInfo } from '../api/auth';
import { Navigation } from '../components/layout/Navigation';

interface InviteStats {
  total: number;
  unused: number;
  used: number;
  expired: number;
}

export default function InvitesPage() {
  const [invites, setInvites] = useState<Invite[]>([]);
  const [stats, setStats] = useState<InviteStats>({ total: 0, unused: 0, used: 0, expired: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<UserInfo | null>(null);
  const [generating, setGenerating] = useState(false);
  const [expiresInDays, setExpiresInDays] = useState<string>('7');
  const [bulkCount, setBulkCount] = useState<number>(5);
  const [isSuperuserInvite, setIsSuperuserInvite] = useState<boolean>(false);
  const [filter, setFilter] = useState<'all' | 'unused' | 'used' | 'expired'>('all');
  const [showConfirmInvalidate, setShowConfirmInvalidate] = useState<number | null>(null);
  const [newlyGeneratedCodes, setNewlyGeneratedCodes] = useState<string[]>([]);

  const navigate = useNavigate();

  useEffect(() => {
    checkAuthAndLoadData();
  }, []);

  // Ensure the select value is properly set
  useEffect(() => {
    setExpiresInDays('7');
  }, []);

  const checkAuthAndLoadData = async () => {
    try {
      const user = await AuthService.getCurrentUser();
      if (!user) {
        navigate('/login');
        return;
      }
      setCurrentUser(user);
      
      if (!user.is_superuser) {
        setError('Only superusers can access invite management');
        setLoading(false);
        return;
      }

      await loadInvites();
    } catch (error) {
      setError('Failed to load user data');
      setLoading(false);
    }
  };

  const loadInvites = async () => {
    try {
      setLoading(true);
      const response = await InviteService.getInvites();
      setInvites(response.invites);
      setStats({
        total: response.total,
        unused: response.unused_count,
        used: response.used_count,
        expired: response.expired_count
      });
    } catch (error: any) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInvite = async () => {
    try {
      setGenerating(true);
      const response = await InviteService.createInvite({ 
        expires_in_days: expiresInDays ? Number(expiresInDays) : undefined,
        is_superuser_invite: isSuperuserInvite
      });
      await loadInvites();
      setNewlyGeneratedCodes([response.code]); // Track the newly generated code
      setExpiresInDays('7'); // Reset to default
      setIsSuperuserInvite(false); // Reset to default
    } catch (error: any) {
      setError(error.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleBulkGenerateInvites = async () => {
    try {
      setGenerating(true);
      const promises = Array.from({ length: bulkCount }, () => 
        InviteService.createInvite({ 
          expires_in_days: expiresInDays ? Number(expiresInDays) : undefined,
          is_superuser_invite: isSuperuserInvite
        })
      );
      const responses = await Promise.all(promises);
      await loadInvites();
      const newCodes = responses.map(response => response.code);
      setNewlyGeneratedCodes(newCodes); // Track the newly generated codes
      setExpiresInDays('7'); // Reset to default
      setIsSuperuserInvite(false); // Reset to default
    } catch (error: any) {
      setError(error.message);
    } finally {
      setGenerating(false);
    }
  };

  const copyNewlyGeneratedCodes = () => {
    if (newlyGeneratedCodes.length === 0) {
      setError('No newly generated codes to copy');
      return;
    }
    
    const codesText = newlyGeneratedCodes.join('\n');
    navigator.clipboard.writeText(codesText);
    // You could add a success toast here
  };

  const handleInvalidateInvite = async (inviteId: number) => {
    try {
      await InviteService.invalidateInvite(inviteId);
      await loadInvites();
      setShowConfirmInvalidate(null);
    } catch (error: any) {
      setError(error.message);
    }
  };

  const getFilteredInvites = () => {
    switch (filter) {
      case 'unused':
        return invites.filter(invite => invite.is_active && !invite.used_by && !invite.is_expired);
      case 'used':
        return invites.filter(invite => invite.used_by);
      case 'expired':
        return invites.filter(invite => invite.is_expired && !invite.used_by);
      default:
        return invites;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (invite: Invite) => {
    if (invite.used_by) {
      return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Used</span>;
    } else if (invite.is_expired) {
      return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Expired</span>;
    } else if (!invite.is_active) {
      return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">Invalidated</span>;
    } else {
      return <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">Active</span>;
    }
  };

  const copyToClipboard = (code: string) => {
    navigator.clipboard.writeText(code);
    // You could add a toast notification here
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading invite codes...</p>
        </div>
      </div>
    );
  }

  if (error && !currentUser?.is_superuser) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl font-semibold mb-4">{error}</div>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Invite Code Management</h1>
          <p className="mt-2 text-slate-300">
            Generate and manage invite codes for new user registration
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError(null)}
                  className="text-red-400 hover:text-red-600"
                >
                  <span className="sr-only">Dismiss</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">Total Codes</dt>
                    <dd className="text-lg font-medium text-white">{stats.total}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">Active</dt>
                    <dd className="text-lg font-medium text-white">{stats.unused}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">Used</dt>
                    <dd className="text-lg font-medium text-white">{stats.used}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">Expired</dt>
                    <dd className="text-lg font-medium text-white">{stats.expired}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Generate New Code */}
        <div className="bg-slate-800 shadow rounded-lg mb-8">
          <div className="px-6 py-4 border-b border-slate-600">
            <h3 className="text-lg font-medium text-white">Generate New Invite Code</h3>
          </div>
          <div className="px-6 py-4">
            <div className="flex flex-col sm:flex-row gap-4 items-end">
              <div className="flex-1">
                <label htmlFor="expiresInDays" className="block text-sm font-medium text-slate-300 mb-2">
                  Expires in (days)
                </label>
                <select
                  id="expiresInDays"
                  value={expiresInDays}
                  onChange={(e) => setExpiresInDays(e.target.value)}
                  className="block w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent sm:text-sm"
                >
                  <option value="">No expiration</option>
                  <option value="1">1 day</option>
                  <option value="3">3 days</option>
                  <option value="7">7 days</option>
                  <option value="14">14 days</option>
                  <option value="30">30 days</option>
                </select>
              </div>
              <div className="flex items-center">
                <input
                  id="superuserInvite"
                  type="checkbox"
                  checked={isSuperuserInvite}
                  onChange={(e) => setIsSuperuserInvite(e.target.checked)}
                  className="h-4 w-4 text-amber-600 focus:ring-amber-500 border-slate-600 rounded bg-slate-800"
                />
                <label htmlFor="superuserInvite" className="ml-2 block text-sm text-slate-300">
                  Create superuser account
                </label>
              </div>
              <button
                onClick={handleGenerateInvite}
                disabled={generating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  'Generate Code'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Bulk Generate Codes */}
        <div className="bg-slate-800 shadow rounded-lg mb-8">
          <div className="px-6 py-4 border-b border-slate-600">
            <h3 className="text-lg font-medium text-white">Bulk Generate Invite Codes</h3>
          </div>
          <div className="px-6 py-4">
            <div className="flex flex-col sm:flex-row gap-4 items-end">
              <div className="flex-1">
                <label htmlFor="bulkCount" className="block text-sm font-medium text-slate-300 mb-2">
                  Number of codes to generate
                </label>
                <input
                  id="bulkCount"
                  type="number"
                  min="1"
                  max="50"
                  value={bulkCount}
                  onChange={(e) => setBulkCount(Math.max(1, Math.min(50, parseInt(e.target.value) || 1)))}
                  className="block w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent sm:text-sm"
                  placeholder="5"
                />
              </div>
              <div className="flex items-center">
                <input
                  id="bulkSuperuserInvite"
                  type="checkbox"
                  checked={isSuperuserInvite}
                  onChange={(e) => setIsSuperuserInvite(e.target.checked)}
                  className="h-4 w-4 text-amber-600 focus:ring-amber-500 border-slate-600 rounded bg-slate-800"
                />
                <label htmlFor="bulkSuperuserInvite" className="ml-2 block text-sm text-slate-300">
                  Create superuser accounts
                </label>
              </div>
              <button
                onClick={handleBulkGenerateInvites}
                disabled={generating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-amber-600 hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  `Generate ${bulkCount} Codes`
                )}
              </button>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <p className="text-sm text-slate-400">
                Uses the same expiration setting as above
              </p>
              <button
                onClick={copyNewlyGeneratedCodes}
                disabled={newlyGeneratedCodes.length === 0}
                className="inline-flex items-center px-3 py-1.5 border border-slate-600 text-sm font-medium rounded-md text-slate-300 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy Newly Generated Codes ({newlyGeneratedCodes.length})
              </button>
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { key: 'all', label: 'All', count: stats.total },
              { key: 'unused', label: 'Active', count: stats.unused },
              { key: 'used', label: 'Used', count: stats.used },
              { key: 'expired', label: 'Expired', count: stats.expired }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  filter === tab.key
                    ? 'border-amber-500 text-amber-400'
                    : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-600'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </nav>
        </div>

        {/* Invite Codes Table */}
        <div className="bg-slate-800 shadow overflow-hidden sm:rounded-md">
                      <ul className="divide-y divide-slate-600">
            {getFilteredInvites().map((invite) => (
              <li key={invite.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-slate-600 flex items-center justify-center">
                        <svg className="h-6 w-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center space-x-2">
                        <code className="text-sm font-mono bg-slate-700 text-white px-2 py-1 rounded border border-slate-600">
                          {invite.code}
                        </code>
                        <button
                          onClick={() => copyToClipboard(invite.code)}
                          className="text-slate-400 hover:text-slate-300"
                          title="Copy to clipboard"
                        >
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </button>
                        {getStatusBadge(invite)}
                        {invite.is_superuser_invite && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
                            Superuser
                          </span>
                        )}
                      </div>
                      <div className="mt-1 text-sm text-slate-400">
                        Created {formatDate(invite.created_at)}
                        {invite.expires_at && (
                          <span className="ml-2">
                            • Expires {formatDate(invite.expires_at)}
                          </span>
                        )}
                        {invite.used_by && invite.used_username && (
                          <span className="ml-2">
                            • Used by {invite.used_username}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {invite.is_active && !invite.used_by && !invite.is_expired && (
                      <button
                        onClick={() => setShowConfirmInvalidate(invite.id)}
                        className="text-red-400 hover:text-red-300 text-sm font-medium"
                      >
                        Invalidate
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
          
          {getFilteredInvites().length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-white">No invite codes</h3>
              <p className="mt-1 text-sm text-slate-400">
                {filter === 'all' 
                  ? 'Get started by generating your first invite code.'
                  : `No ${filter} invite codes found.`
                }
              </p>
            </div>
          )}
        </div>

        {/* Invalidation Confirmation Modal */}
        {showConfirmInvalidate && (
          <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border border-slate-600 w-96 shadow-lg rounded-md bg-slate-800">
              <div className="mt-3 text-center">
                <h3 className="text-lg font-medium text-white mb-4">Confirm Invalidation</h3>
                <p className="text-sm text-slate-300 mb-6">
                  Are you sure you want to invalidate this invite code? This action cannot be undone.
                </p>
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => setShowConfirmInvalidate(null)}
                    className="px-4 py-2 bg-slate-600 text-slate-200 rounded-md hover:bg-slate-500"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleInvalidateInvite(showConfirmInvalidate)}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    Invalidate
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 