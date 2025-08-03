import apiClient from './config';

export interface VersionInfo {
  version: string;
  app_name: string;
  environment: string;
  build_date: string;
  git_commit: string;
}

/**
 * Fetch version information from the API
 */
export const getVersion = async (): Promise<VersionInfo> => {
  try {
    const response = await apiClient.get<VersionInfo>('/version');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch version:', error);
    // Return fallback version info
    return {
      version: '0.1.0',
      app_name: 'GuildRoster',
      environment: 'unknown',
      build_date: new Date().toISOString(),
      git_commit: 'unknown'
    };
  }
}; 