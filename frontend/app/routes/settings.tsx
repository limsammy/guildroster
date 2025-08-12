import React from 'react';
import { Link } from 'react-router';
import { Button, Card, Container, GuildSwitcher } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import { exportResourcesAsZip } from '../utils/exportZip';
import { exportAllAsJson, copyAllAsJson } from '../utils/exportJson';
import { importResourcesFromFile, validateImportedData } from '../utils/importZip';
import { ImportService } from '../api/import';
import { RaidService } from '../api/raids';
import { TeamService } from '../api/teams';
import { ToonService } from '../api/toons';
import { GuildService } from '../api/guilds';
import { ScenarioService } from '../api/scenarios';
import { AttendanceService } from '../api/attendance';

export function meta() {
  return [
    { title: 'Settings - GuildRoster' },
    { name: 'description', content: 'Manage guild settings, scenarios, and administrative functions.' },
  ];
}

export default function Settings() {
  const { user } = useAuth();

  // Export section state
  const [selectedResources, setSelectedResources] = React.useState<string[]>([]);
  const [exportEnabled, setExportEnabled] = React.useState(false);
  const [loadingExportStatus, setLoadingExportStatus] = React.useState(true);
  
  // Import section state
  const [importFile, setImportFile] = React.useState<File | null>(null);
  const [importLoading, setImportLoading] = React.useState(false);
  const [importResult, setImportResult] = React.useState<{ success: boolean; message: string; errors?: string[] } | null>(null);
  const [copyResult, setCopyResult] = React.useState<string | null>(null);
  const allResources = [
    { key: 'raids', label: 'Raids' },
    { key: 'teams', label: 'Teams' },
    { key: 'toons', label: 'Characters' },
    { key: 'guilds', label: 'Guilds' },
    { key: 'scenarios', label: 'Scenarios' },
  ];
  const allKeys = allResources.map(r => r.key);
  const allSelected = selectedResources.length === allResources.length;

  const handleSelect = (key: string) => {
    setSelectedResources(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };
  const handleSelectAll = () => {
    setSelectedResources(allSelected ? [] : allKeys);
  };

  const resourceFetchers: { [key: string]: () => Promise<any> } = {
    raids: RaidService.getRaids,
    teams: TeamService.getTeams,
    toons: ToonService.getToons,
    guilds: GuildService.getGuilds,
    scenarios: ScenarioService.getScenarios,
  };

  const handleExport = async () => {
    await exportResourcesAsZip(resourceFetchers, selectedResources);
  };

  const handleExportJson = async () => {
    await exportAllAsJson(resourceFetchers, selectedResources);
  };

  const handleCopyJson = async () => {
    try {
      const jsonString = await copyAllAsJson(resourceFetchers, selectedResources);
      setCopyResult('Data copied to clipboard!');
      setTimeout(() => setCopyResult(null), 3000);
    } catch (error) {
      console.error('Failed to copy data:', error);
      setCopyResult('Failed to copy to clipboard. Please try downloading instead.');
      setTimeout(() => setCopyResult(null), 3000);
    }
  };

  const handleImport = async () => {
    if (!importFile) return;
    
    setImportLoading(true);
    setImportResult(null);
    
    try {
      // First validate the file structure
      const validationResult = await importResourcesFromFile(importFile);
      if (!validationResult.success) {
        setImportResult(validationResult);
        return;
      }
      
      if (validationResult.importedData) {
        const validation = validateImportedData(validationResult.importedData);
        if (!validation.valid) {
          setImportResult({
            success: false,
            message: 'Validation failed',
            errors: validation.errors
          });
          return;
        }
      }
      
      // If validation passes, send to backend
      const apiResult = await ImportService.importData(importFile);
      
      // Format the API response for display
      const errors: string[] = [];
      Object.entries(apiResult.results).forEach(([type, result]) => {
        if (result.errors.length > 0) {
          errors.push(`${type}: ${result.errors.join(', ')}`);
        }
      });
      
      setImportResult({
        success: errors.length === 0,
        message: apiResult.message,
        errors: errors.length > 0 ? errors : undefined
      });
      
    } catch (error: any) {
      setImportResult({
        success: false,
        message: `Import failed: ${error.response?.data?.detail || error.message}`,
        errors: [error.response?.data?.detail || error.message]
      });
    } finally {
      setImportLoading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setImportFile(file || null);
    setImportResult(null);
  };

  // Check export status on component mount
  React.useEffect(() => {
    const checkExportStatus = async () => {
      try {
        const enabled = await AttendanceService.isExportEnabled();
        setExportEnabled(enabled);
      } catch (error) {
        console.error('Failed to check export status:', error);
        setExportEnabled(false);
      } finally {
        setLoadingExportStatus(false);
      }
    };
    
    checkExportStatus();
  }, []);

  // Only show settings for superusers
  if (!user?.is_superuser) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
          <p className="text-slate-300 mb-4">You don't have permission to access settings.</p>
          <Link to="/dashboard">
            <Button variant="primary">Return to Dashboard</Button>
          </Link>
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
                  <span className="text-slate-300">Settings</span>
                </nav>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Settings</h1>
                <p className="text-slate-300 mt-1">Manage guild settings and administrative functions</p>
              </div>
              <div className="flex gap-3">
                <Link to="/dashboard">
                  <Button variant="secondary">Dashboard</Button>
                </Link>
              </div>
            </div>
          </div>
        </Container>
      </div>

      <Container>
        <div className="py-8">
          {/* Guild Management Section */}
          <Card variant="elevated" className="p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">Guild Management</h2>
                <p className="text-slate-300 mt-1">Manage guilds and switch between them</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Guild Switcher */}
              <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4">
                <h3 className="font-semibold text-white mb-3">Current Guild</h3>
                <GuildSwitcher />
              </div>
              
              {/* Manage Guilds */}
              <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4">
                <h3 className="font-semibold text-white mb-3">Guild Administration</h3>
                <p className="text-slate-300 text-sm mb-4">
                  Create, edit, and manage guilds in the system.
                </p>
                <Link to="/guilds">
                  <Button variant="primary" className="w-full">
                    Manage Guilds
                  </Button>
                </Link>
              </div>
            </div>
          </Card>

          {/* Content Management Section */}
          <Card variant="elevated" className="p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">Content Management</h2>
                <p className="text-slate-300 mt-1">Manage scenarios and game content</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Scenarios */}
              <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4 flex flex-col justify-between">
                <div>
                  <div className="text-3xl mb-3">🎮</div>
                  <h3 className="font-semibold text-white mb-2">Scenarios</h3>
                  <p className="text-slate-300 text-sm">
                    Manage game scenarios and their availability for raids.
                  </p>
                </div>
                <Link to="/scenarios" className="mt-4">
                  <Button variant="primary" className="w-full">
                    Manage Scenarios
                  </Button>
                </Link>
              </div>

              {/* Teams */}
              <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4 flex flex-col justify-between">
                <div>
                  <div className="text-3xl mb-3">👥</div>
                  <h3 className="font-semibold text-white mb-2">Teams</h3>
                  <p className="text-slate-300 text-sm">
                    Manage raid teams and their compositions.
                  </p>
                </div>
                <Link to="/teams" className="mt-4">
                  <Button variant="primary" className="w-full">
                    Manage Teams
                  </Button>
                </Link>
              </div>

              {/* Characters */}
              <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4 flex flex-col justify-between">
                <div>
                  <div className="text-3xl mb-3">⚔️</div>
                  <h3 className="font-semibold text-white mb-2">Characters</h3>
                  <p className="text-slate-300 text-sm">
                    Manage character profiles and their team assignments.
                  </p>
                </div>
                <Link to="/toons" className="mt-4">
                  <Button variant="primary" className="w-full">
                    Manage Characters
                  </Button>
                </Link>
              </div>
            </div>
          </Card>

          {/* Export Data Section */}
          <Card variant="elevated" className="p-6 mb-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">Export Data</h2>
              <p className="text-slate-300 mb-4">Select one or more resources to export in different formats.</p>
              <div className="mb-4">
                <label className="flex items-center mb-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={handleSelectAll}
                    className="w-4 h-4 text-amber-500 bg-slate-800 border-slate-600 rounded focus:ring-amber-500 focus:ring-2 mr-2"
                  />
                  <span className="text-slate-200 font-medium">Select All</span>
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {allResources.map(resource => (
                    <label key={resource.key} className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedResources.includes(resource.key)}
                        onChange={() => handleSelect(resource.key)}
                        className="w-4 h-4 text-amber-500 bg-slate-800 border-slate-600 rounded focus:ring-amber-500 focus:ring-2 mr-2"
                      />
                      <span className="text-slate-200">{resource.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button
                  variant="primary"
                  onClick={handleExport}
                  disabled={selectedResources.length === 0}
                >
                  Export as ZIP
                </Button>
                <Button
                  variant="secondary"
                  onClick={handleExportJson}
                  disabled={selectedResources.length === 0}
                >
                  Export as JSON
                </Button>
                <Button
                  variant="secondary"
                  onClick={handleCopyJson}
                  disabled={selectedResources.length === 0}
                >
                  Copy to Clipboard
                </Button>
              </div>
              {copyResult && (
                <div className={`mt-3 p-3 rounded-lg text-sm ${copyResult.includes('Failed') ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                  {copyResult}
                </div>
              )}
            </div>
          </Card>

          {/* Import Data Section */}
          <Card variant="elevated" className="p-6 mb-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">Import Data</h2>
              <p className="text-slate-300 mb-4">Import data from exported ZIP or JSON files. This will add new records to your database.</p>
              
              <div className="mb-4">
                <input
                  type="file"
                  accept=".zip,.json"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-amber-500 file:text-white hover:file:bg-amber-600 file:cursor-pointer"
                />
                <p className="text-slate-400 text-xs mt-2">
                  Supported formats: ZIP files with JSON data or single JSON files
                </p>
              </div>
              
              <Button
                variant="primary"
                onClick={handleImport}
                disabled={!importFile || importLoading}
              >
                {importLoading ? 'Importing...' : 'Import Data'}
              </Button>
              
              {importResult && (
                <div className={`mt-4 p-4 rounded-lg ${importResult.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  <div className="font-medium mb-2">{importResult.message}</div>
                  {importResult.errors && importResult.errors.length > 0 && (
                    <div className="text-sm">
                      <div className="font-medium mb-1">Errors:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {importResult.errors.map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </Card>

          {/* Feature Flags Section */}
          <Card variant="elevated" className="p-6 mb-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">Feature Flags</h2>
              <p className="text-slate-300 mb-4">Enable or disable specific features in the application.</p>
              
              <div className="space-y-4">
                {/* Attendance Export Toggle */}
                <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-white mb-1">Attendance Export</h3>
                      <p className="text-slate-300 text-sm">
                        Allow users to export attendance reports as PNG images
                      </p>
                    </div>
                    <div className="flex items-center">
                      {loadingExportStatus ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-amber-500"></div>
                      ) : (
                        <div className="flex items-center">
                          <span className={`text-sm font-medium mr-3 ${exportEnabled ? 'text-green-400' : 'text-red-400'}`}>
                            {exportEnabled ? 'Enabled' : 'Disabled'}
                          </span>
                          <div className="text-slate-400 text-xs">
                            Set via ENABLE_ATTENDANCE_EXPORT environment variable
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* System Information */}
          <Card variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">System Information</h2>
                <p className="text-slate-300 mt-1">Current user and system details</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* User Info */}
              <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4">
                <h3 className="font-semibold text-white mb-3">Current User</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Username:</span>
                    <span className="text-white font-medium">{user?.username}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">User ID:</span>
                    <span className="text-white font-medium">{user?.user_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Role:</span>
                    <span className="text-amber-400 font-medium">
                      {user?.is_superuser ? 'Superuser' : 'User'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-slate-800/50 rounded-lg border border-slate-600/30 p-4">
                <h3 className="font-semibold text-white mb-3">Quick Actions</h3>
                <div className="space-y-3">
                  <Link to="/toons">
                    <Button variant="secondary" className="w-full">
                      Manage Toons
                    </Button>
                  </Link>
                  <Link to="/dashboard">
                    <Button variant="secondary" className="w-full">
                      Back to Dashboard
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </Container>
    </div>
  );
} 