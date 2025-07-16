import React from 'react';
import { Container } from '../ui/Container';

export const Footer: React.FC = () => {
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
              © 2024 GuildRoster. All rights reserved.
            </p>
            <p className="text-slate-400 text-sm mt-2 md:mt-0">
              For the Horde! For the Alliance!
            </p>
          </div>
        </div>
      </Container>
    </footer>
  );
}; 