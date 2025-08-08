import apiClient from './config';
import type { 
  Attendance, 
  AttendanceCreate, 
  AttendanceUpdate, 
  AttendanceBulkCreate, 
  AttendanceBulkUpdate,
  AttendanceStats,
  AttendanceFilters,
  BenchedPlayer,
  TeamViewData
} from './types';

export class AttendanceService {
  // Get attendance records with optional filtering
  static async getAttendance(filters?: AttendanceFilters): Promise<Attendance[]> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const url = params.toString() ? `/attendance/?${params.toString()}` : '/attendance/';
    const response = await apiClient.get<Attendance[]>(url);
    return response.data;
  }

  // Get attendance by ID
  static async getAttendanceById(attendanceId: number): Promise<Attendance> {
    const response = await apiClient.get<Attendance>(`/attendance/${attendanceId}`);
    return response.data;
  }

  // Get attendance by raid ID
  static async getAttendanceByRaid(raidId: number): Promise<Attendance[]> {
    const response = await apiClient.get<Attendance[]>(`/attendance/raid/${raidId}`);
    return response.data;
  }

  // Get attendance by toon ID
  static async getAttendanceByToon(toonId: number): Promise<Attendance[]> {
    const response = await apiClient.get<Attendance[]>(`/attendance/toon/${toonId}`);
    return response.data;
  }



  // Get attendance by team ID
  static async getAttendanceByTeam(teamId: number): Promise<Attendance[]> {
    const response = await apiClient.get<Attendance[]>(`/attendance/team/${teamId}`);
    return response.data;
  }

  // Create single attendance record
  static async createAttendance(attendanceData: AttendanceCreate): Promise<Attendance> {
    const response = await apiClient.post<Attendance>('/attendance/', attendanceData);
    return response.data;
  }

  // Create multiple attendance records
  static async createBulkAttendance(bulkData: AttendanceBulkCreate): Promise<Attendance[]> {
    const response = await apiClient.post<Attendance[]>('/attendance/bulk', bulkData);
    return response.data;
  }

  // Update attendance record
  static async updateAttendance(attendanceId: number, attendanceData: AttendanceUpdate): Promise<Attendance> {
    const response = await apiClient.put<Attendance>(`/attendance/${attendanceId}`, attendanceData);
    return response.data;
  }

  // Update multiple attendance records
  static async updateBulkAttendance(bulkData: AttendanceBulkUpdate): Promise<Attendance[]> {
    const response = await apiClient.put<Attendance[]>('/attendance/bulk', bulkData);
    return response.data;
  }

  // Delete attendance record
  static async deleteAttendance(attendanceId: number): Promise<void> {
    await apiClient.delete(`/attendance/${attendanceId}`);
  }

  // Get attendance statistics for raid
  static async getRaidStats(raidId: number): Promise<AttendanceStats> {
    const response = await apiClient.get<AttendanceStats>(`/attendance/stats/raid/${raidId}`);
    return response.data;
  }

  // Get attendance statistics for toon
  static async getToonStats(toonId: number): Promise<AttendanceStats> {
    const response = await apiClient.get<AttendanceStats>(`/attendance/stats/toon/${toonId}`);
    return response.data;
  }



  // Get attendance statistics for team
  static async getTeamStats(teamId: number): Promise<AttendanceStats> {
    const response = await apiClient.get<AttendanceStats>(`/attendance/stats/team/${teamId}`);
    return response.data;
  }

  // Get attendance report for date range
  static async getAttendanceReport(startDate: string, endDate: string): Promise<Attendance[]> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate
    });
    
    const response = await apiClient.get<Attendance[]>(`/attendance/report/date-range?${params.toString()}`);
    return response.data;
  }

  // Get benched players for a team in a specific week
  static async getBenchedPlayers(teamId: number, weekDate: string): Promise<BenchedPlayer[]> {
    const response = await apiClient.get<BenchedPlayer[]>(`/attendance/benched/team/${teamId}/week/${weekDate}`);
    return response.data;
  }

  // Get team attendance view with toons as rows and raids as columns
  static async getTeamAttendanceView(
    teamId: number, 
    raidCount: number = 5, 
    guildId?: number
  ): Promise<TeamViewData> {
    const params = new URLSearchParams({
      raid_count: raidCount.toString()
    });
    
    if (guildId) {
      params.append('guild_id', guildId.toString());
    }
    
    const response = await apiClient.get<TeamViewData>(`/attendance/team-view/${teamId}?${params.toString()}`);
    return response.data;
  }

  // Export team attendance as image
  static async exportTeamImage(
    teamId: number,
    period: 'current' | 'all' | 'custom' = 'current',
    startDate?: string,
    endDate?: string,
    raidCount: number = 20
  ): Promise<Blob> {
    const params = new URLSearchParams({
      period,
      raid_count: raidCount.toString()
    });
    
    if (startDate) {
      params.append('start_date', startDate);
    }
    if (endDate) {
      params.append('end_date', endDate);
    }
    
    const url = `/attendance/export/team/${teamId}/image?${params.toString()}`;
    console.log('Export team image URL:', url);
    console.log('Full URL:', `${apiClient.defaults.baseURL}${url}`);
    
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob'
      });
      console.log('Export team image response:', response.status, response.statusText);
      return response.data;
    } catch (error) {
      console.error('Export team image error:', error);
      throw error;
    }
  }

  // Export all teams attendance as ZIP
  static async exportAllTeamsImages(
    guildId?: number,
    period: 'current' | 'all' | 'custom' = 'current',
    startDate?: string,
    endDate?: string,
    raidCount: number = 20
  ): Promise<Blob> {
    const params = new URLSearchParams({
      period,
      raid_count: raidCount.toString()
    });
    
    if (guildId) {
      params.append('guild_id', guildId.toString());
    }
    if (startDate) {
      params.append('start_date', startDate);
    }
    if (endDate) {
      params.append('end_date', endDate);
    }
    
    const response = await apiClient.get(`/attendance/export/all-teams/image?${params.toString()}`, {
      responseType: 'blob'
    });
    return response.data;
  }
} 