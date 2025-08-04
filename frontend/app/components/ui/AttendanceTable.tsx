import React from 'react';
import type { TeamViewData, ToonAttendanceRecord } from '../../api/types';

interface AttendanceTableProps {
  data: TeamViewData;
  className?: string;
}

export function AttendanceTable({ data, className = '' }: AttendanceTableProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present':
        return 'bg-green-600/20 text-green-400 border-green-600/30';
      case 'absent':
        return 'bg-red-600/20 text-red-400 border-red-600/30';
      case 'benched':
        return 'bg-yellow-600/20 text-yellow-400 border-yellow-600/30';
      default:
        return 'bg-slate-600/20 text-slate-400 border-slate-600/30';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'present':
        return '✓';
      case 'absent':
        return '✗';
      case 'benched':
        return 'B';
      default:
        return '?';
    }
  };

  const getTooltipContent = (record: ToonAttendanceRecord) => {
    const parts = [];
    
    if (record.notes) {
      parts.push(`Notes: ${record.notes}`);
    }
    
    if (record.benched_note) {
      parts.push(`Benched Note: ${record.benched_note}`);
    }
    
    if (parts.length === 0) {
      parts.push('No notes');
    }
    
    return parts.join('\n');
  };

  if (!data.toons.length || !data.raids.length) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <div className="text-slate-400 text-6xl mb-4">📊</div>
        <h3 className="text-xl font-semibold text-white mb-2">No attendance data</h3>
        <p className="text-slate-400">
          No toons or raids found for the selected team and time period.
        </p>
      </div>
    );
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-slate-600">
            {/* Toon info columns */}
            <th className="text-left p-3 text-slate-300 font-medium sticky left-0 bg-slate-900 z-10">
              Toon
            </th>
            <th className="text-left p-3 text-slate-300 font-medium sticky left-20 bg-slate-900 z-10">
              Class
            </th>
            <th className="text-left p-3 text-slate-300 font-medium sticky left-32 bg-slate-900 z-10">
              Role
            </th>
            <th className="text-left p-3 text-slate-300 font-medium sticky left-44 bg-slate-900 z-10">
              Attendance %
            </th>
            
            {/* Raid columns */}
            {data.raids.map(raid => (
              <th key={raid.id} className="text-center p-3 text-slate-300 font-medium min-w-[80px]">
                <div className="flex flex-col items-center">
                  <div className="text-xs text-slate-400 mb-1">
                    {formatDate(raid.scheduled_at)}
                  </div>
                  <div className="text-xs">
                    {raid.scenario_name}
                  </div>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.toons.map(toon => (
            <tr key={toon.id} className="border-b border-slate-700 hover:bg-slate-800/50">
              {/* Toon info cells */}
              <td className="p-3 text-white font-medium sticky left-0 bg-slate-900 z-10">
                {toon.username}
              </td>
              <td className="p-3 text-slate-300 sticky left-20 bg-slate-900 z-10">
                {toon.class_name}
              </td>
              <td className="p-3 text-slate-300 sticky left-32 bg-slate-900 z-10">
                {toon.role}
              </td>
              <td className="p-3 text-slate-300 sticky left-44 bg-slate-900 z-10">
                <span className={`font-medium ${
                  toon.overall_attendance_percentage >= 80 ? 'text-green-400' :
                  toon.overall_attendance_percentage >= 60 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {toon.overall_attendance_percentage.toFixed(1)}%
                </span>
              </td>
              
              {/* Attendance cells */}
              {data.raids.map(raid => {
                const record = toon.attendance_records.find(r => r.raid_id === raid.id);
                const hasNote = record?.has_note || false;
                const isBenchedWithNote = record?.status === 'benched' && hasNote;
                
                return (
                  <td key={raid.id} className="p-2 text-center">
                    {record ? (
                      <div
                        className={`inline-flex items-center justify-center w-8 h-8 rounded border text-sm font-medium cursor-help relative ${
                          getStatusColor(record.status)
                        }`}
                        title={getTooltipContent(record)}
                      >
                        {getStatusText(record.status)}
                        {isBenchedWithNote && (
                          <span className="absolute -top-1 -right-1 text-xs text-yellow-400">*</span>
                        )}
                      </div>
                    ) : (
                      <div className="w-8 h-8 flex items-center justify-center text-slate-500">
                        -
                      </div>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Legend */}
      <div className="mt-6 p-4 bg-slate-800/50 rounded-lg">
        <h4 className="text-sm font-medium text-slate-300 mb-3">Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-green-600/20 text-green-400 border border-green-600/30 rounded flex items-center justify-center text-xs font-medium">
              ✓
            </div>
            <span className="text-slate-300">Present</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-red-600/20 text-red-400 border border-red-600/30 rounded flex items-center justify-center text-xs font-medium">
              ✗
            </div>
            <span className="text-slate-300">Absent</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-yellow-600/20 text-yellow-400 border border-yellow-600/30 rounded flex items-center justify-center text-xs font-medium">
              B
            </div>
            <span className="text-slate-300">Benched</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-yellow-600/20 text-yellow-400 border border-yellow-600/30 rounded flex items-center justify-center text-xs font-medium relative">
              B
              <span className="absolute -top-1 -right-1 text-xs text-yellow-400">*</span>
            </div>
            <span className="text-slate-300">Benched with note</span>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Hover over attendance cells to view notes. Attendance percentage excludes benched raids from calculation.
        </p>
      </div>
    </div>
  );
} 