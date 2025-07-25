// User Types
export interface User {
  id: number;
  username: string;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  password: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface UserLoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
  is_superuser: boolean;
}

// Token Types
export interface Token {
  id: number;
  key: string;
  name: string;
  type: 'user' | 'system' | 'api';
  user_id?: number;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TokenCreate {
  name: string;
  type: 'user' | 'system' | 'api';
  user_id?: number;
  expires_days?: number;
}

// Guild Types
export interface Guild {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface GuildCreate {
  name: string;
}

export interface GuildUpdate {
  name?: string;
}

// Team Types
export interface Team {
  id: number;
  name: string;
  guild_id: number;
  created_at: string;
  updated_at: string;
}

export interface TeamCreate {
  name: string;
  guild_id: number;
}

export interface TeamUpdate {
  name?: string;
  guild_id?: number;
}

// Toon Types
export interface Toon {
  id: number;
  username: string;
  class: string;
  role: string;
  team_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface ToonCreate {
  username: string;
  class: string;
  role: string;
  team_ids?: number[];
}

export interface ToonUpdate {
  username?: string;
  class?: string;
  role?: string;
  team_ids?: number[];
}

// Scenario Types
export interface Scenario {
  id: number;
  name: string;
  is_active: boolean;
  mop: boolean;
  created_at: string;
  updated_at: string;
}

export interface ScenarioCreate {
  name: string;
  is_active?: boolean;
  mop?: boolean;
}

export interface ScenarioUpdate {
  name?: string;
  is_active?: boolean;
  mop?: boolean;
}

// Scenario Variation Types (for the templating system)
export interface ScenarioVariation {
  name: string;
  difficulty: string;
  size: string;
  display_name: string;
  variation_id: string;
}

export interface ScenarioWithVariations extends Scenario {
  variations: ScenarioVariation[];
}

// Raid Types
export interface Raid {
  id: number;
  scheduled_at: string;
  team_id: number;
  scenario_name: string;
  scenario_difficulty: string;
  scenario_size: string;
  warcraftlogs_url?: string;
  warcraftlogs_report_code?: string;
  warcraftlogs_metadata?: Record<string, any>;
  warcraftlogs_participants?: Record<string, any>[];
  warcraftlogs_fights?: Record<string, any>[];
  created_at: string;
  updated_at: string;
}

export interface RaidCreate {
  scheduled_at: string;
  team_id: number;
  scenario_name: string;
  scenario_difficulty: string;
  scenario_size: string;
  warcraftlogs_url?: string;
}

export interface RaidUpdate {
  scheduled_at?: string;
  team_id?: number;
  scenario_name?: string;
  scenario_difficulty?: string;
  scenario_size?: string;
  warcraftlogs_url?: string;
}

// WarcraftLogs Types
export interface WarcraftLogsParticipant {
  id: string;
  canonicalID: string;
  name: string;
  class: string;
  classID: number;
  role: string;
}

export interface WarcraftLogsReportMetadata {
  title: string;
  startTime: number;
  endTime: number;
  owner: { name: string };
  zone: { name: string };
}

export interface MatchedParticipant {
  toon: {
    id: number;
    username: string;
    class: string;
    role: string;
  };
  participant: WarcraftLogsParticipant;
  is_present: boolean;
  notes: string;
}

export interface UnknownParticipant {
  participant: WarcraftLogsParticipant;
  notes: string;
}

export interface AttendanceRecord {
  toon_id: number;
  is_present: boolean;
  notes: string;
}

export interface WarcraftLogsProcessingResult {
  success: boolean;
  report_metadata: WarcraftLogsReportMetadata;
  participants: WarcraftLogsParticipant[];
  matched_participants: MatchedParticipant[];
  unknown_participants: UnknownParticipant[];
  attendance_records: AttendanceRecord[];
  team_toons: Array<{
    id: number;
    username: string;
    class: string;
    role: string;
    is_main: boolean;
  }>;
  error?: string;
}

// Attendance Types
export interface Attendance {
  id: number;
  raid_id: number;
  toon_id: number;
  is_present: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface AttendanceCreate {
  raid_id: number;
  toon_id: number;
  is_present: boolean;
  notes?: string;
}

export interface AttendanceUpdate {
  raid_id?: number;
  toon_id?: number;
  is_present?: boolean;
  notes?: string;
}

export interface AttendanceBulkCreate {
  attendance_records: AttendanceCreate[];
}

export interface AttendanceBulkUpdate {
  attendance_records: AttendanceUpdate[];
}

// Statistics Types
export interface AttendanceStats {
  total_raids: number;
  raids_attended: number;
  raids_missed: number;
  attendance_percentage: number;
  current_streak: number;
  longest_streak: number;
  last_attendance?: string;
}

// Pagination Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Filter Types
export interface AttendanceFilters {
  raid_id?: number;
  toon_id?: number;
  team_id?: number;
  is_present?: boolean;
  start_date?: string;
  end_date?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
} 