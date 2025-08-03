import { useState, useEffect } from 'react';
import { getVersion, type VersionInfo } from '../api/version';

export const useVersion = () => {
  const [version, setVersion] = useState<VersionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVersion = async () => {
      try {
        setLoading(true);
        setError(null);
        const versionInfo = await getVersion();
        setVersion(versionInfo);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch version');
        console.error('Error fetching version:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchVersion();
  }, []);

  return { version, loading, error };
}; 