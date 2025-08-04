import React from 'react';

interface RaidCountSelectorProps {
  raidCount: number;
  onRaidCountChange: (count: number) => void;
  className?: string;
}

export function RaidCountSelector({ raidCount, onRaidCountChange, className = '' }: RaidCountSelectorProps) {
  const raidCountOptions = [5, 10, 15, 20];

  return (
    <select
      value={raidCount}
      onChange={(e) => onRaidCountChange(Number(e.target.value))}
      className={`w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent ${className}`}
    >
      {raidCountOptions.map(count => (
        <option key={count} value={count}>
          Last {count} raids
        </option>
      ))}
    </select>
  );
} 