import React from 'react';
import { Container } from '../ui/Container';
import { useVersion } from '../../hooks/useVersion';

export const Footer: React.FC = () => {
  const { version, loading } = useVersion();
  return (
    <footer className="bg-slate-900/80 backdrop-blur-md border-t border-slate-700/50">
      <Container>
        <div className="py-12">
          <div className="text-center">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent mb-4">
              GuildRoster
            </h3>
            <p className="text-slate-300 mb-4 max-w-md mx-auto">
              Command your guild's destiny with precision. Track attendance, manage rosters, and lead your team to victory in Azeroth's greatest challenges.
            </p>
          </div>

          {/* Bottom */}
          <div className="border-t border-slate-700/50 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-slate-400 text-sm">
              © 2025 GuildRoster. All rights reserved.
            </p>
            <div className="flex flex-col md:flex-row items-center gap-4 mt-2 md:mt-0">
              <p className="text-slate-400 text-sm">
                For the Horde! For the Alliance!
              </p>
              {!loading && version && (
                <p className="text-slate-500 text-xs">
                  v{version.version}
                </p>
              )}
            </div>
          </div>
        </div>
      </Container>
    </footer>
  );
}; 