import apiClient from './config';
import type { Scenario, ScenarioCreate, ScenarioUpdate } from './types';

export class ScenarioService {
  // Get all scenarios
  static async getScenarios(): Promise<Scenario[]> {
    const response = await apiClient.get<Scenario[]>('/scenarios/');
    return response.data;
  }

  // Get scenario by ID
  static async getScenario(scenarioId: number): Promise<Scenario> {
    const response = await apiClient.get<Scenario>(`/scenarios/${scenarioId}`);
    return response.data;
  }

  // Get active scenarios only
  static async getActiveScenarios(): Promise<Scenario[]> {
    const response = await apiClient.get<Scenario[]>('/scenarios/active');
    return response.data;
  }

  // Create new scenario
  static async createScenario(scenarioData: ScenarioCreate): Promise<Scenario> {
    const response = await apiClient.post<Scenario>('/scenarios/', scenarioData);
    return response.data;
  }

  // Update scenario
  static async updateScenario(scenarioId: number, scenarioData: ScenarioUpdate): Promise<Scenario> {
    const response = await apiClient.put<Scenario>(`/scenarios/${scenarioId}`, scenarioData);
    return response.data;
  }

  // Delete scenario
  static async deleteScenario(scenarioId: number): Promise<void> {
    await apiClient.delete(`/scenarios/${scenarioId}`);
  }
} 