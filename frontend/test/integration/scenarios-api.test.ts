import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import axios from 'axios';
import { ScenarioService } from '../../app/api/scenarios';
import type { Scenario, ScenarioCreate, ScenarioUpdate } from '../../app/api/types';

// Test authentication token
const TEST_TOKEN = 'IcRZUmCL0thQtbJkcqIfal52Ujw9xdcR9mPCy69Wv0M';

// Create a test-specific API client
const testApiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${TEST_TOKEN}`,
  },
});

// Test data
const testScenario: ScenarioCreate = {
  name: 'Test Scenario',
  difficulty: 'Normal',
  size: '10',
  is_active: true,
};

const updatedScenario: ScenarioUpdate = {
  name: 'Updated Test Scenario',
  difficulty: 'Heroic',
  size: '25',
  is_active: false,
};

// Create test-specific service functions
const TestScenarioService = {
  async getScenarios(): Promise<Scenario[]> {
    const response = await testApiClient.get<Scenario[]>('/scenarios/');
    return response.data;
  },

  async getActiveScenarios(): Promise<Scenario[]> {
    const response = await testApiClient.get<Scenario[]>('/scenarios/active');
    return response.data;
  },

  async getScenario(id: number): Promise<Scenario> {
    const response = await testApiClient.get<Scenario>(`/scenarios/${id}`);
    return response.data;
  },

  async createScenario(scenarioData: ScenarioCreate): Promise<Scenario> {
    const response = await testApiClient.post<Scenario>('/scenarios/', scenarioData);
    return response.data;
  },

  async updateScenario(id: number, scenarioData: ScenarioUpdate): Promise<Scenario> {
    const response = await testApiClient.put<Scenario>(`/scenarios/${id}`, scenarioData);
    return response.data;
  },

  async deleteScenario(id: number): Promise<void> {
    await testApiClient.delete(`/scenarios/${id}`);
  },
};

describe('Scenarios API Integration Tests', () => {
  let createdScenario: Scenario;

  beforeAll(async () => {
    // Ensure we have a clean state by deleting any test scenarios
    try {
      const scenarios = await TestScenarioService.getScenarios();
      const testScenarios = scenarios.filter(s => 
        s.name.includes('Test Scenario') || s.name.includes('Updated Test Scenario')
      );
      for (const scenario of testScenarios) {
        await TestScenarioService.deleteScenario(scenario.id);
      }
    } catch (error) {
      // Ignore errors during cleanup
    }
  });

  afterAll(async () => {
    // Clean up test data
    try {
      if (createdScenario) {
        await TestScenarioService.deleteScenario(createdScenario.id);
      }
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('GET /scenarios/', () => {
    it('should fetch all scenarios', async () => {
      const scenarios = await TestScenarioService.getScenarios();
      
      expect(Array.isArray(scenarios)).toBe(true);
      scenarios.forEach(scenario => {
        expect(scenario).toHaveProperty('id');
        expect(scenario).toHaveProperty('name');
        expect(scenario).toHaveProperty('is_active');
        expect(scenario).toHaveProperty('created_at');
        expect(scenario).toHaveProperty('updated_at');
        expect(typeof scenario.id).toBe('number');
        expect(typeof scenario.name).toBe('string');
        expect(typeof scenario.is_active).toBe('boolean');
        expect(typeof scenario.created_at).toBe('string');
        expect(typeof scenario.updated_at).toBe('string');
      });
    });
  });

  describe('GET /scenarios/active', () => {
    it('should fetch only active scenarios', async () => {
      const activeScenarios = await TestScenarioService.getActiveScenarios();
      
      expect(Array.isArray(activeScenarios)).toBe(true);
      activeScenarios.forEach(scenario => {
        expect(scenario.is_active).toBe(true);
      });
    });
  });

  describe('POST /scenarios/', () => {
    it('should create a new scenario', async () => {
      createdScenario = await TestScenarioService.createScenario(testScenario);
      
      expect(createdScenario).toHaveProperty('id');
      expect(createdScenario).toHaveProperty('name', testScenario.name);
      expect(createdScenario).toHaveProperty('is_active', testScenario.is_active);
      expect(createdScenario).toHaveProperty('created_at');
      expect(createdScenario).toHaveProperty('updated_at');
      expect(typeof createdScenario.id).toBe('number');
      expect(createdScenario.id).toBeGreaterThan(0);
    });

    it('should create a scenario with default is_active value', async () => {
      const scenarioData: ScenarioCreate = {
        name: 'Test Scenario Default Active',
        difficulty: 'Normal',
        size: '10',
      };
      
      const scenario = await TestScenarioService.createScenario(scenarioData);
      
      expect(scenario.is_active).toBe(true);
      
      // Clean up
      await TestScenarioService.deleteScenario(scenario.id);
    });

    it('should create an inactive scenario', async () => {
      const scenarioData: ScenarioCreate = {
        name: 'Test Scenario Inactive',
        difficulty: 'Challenge',
        size: '25',
        is_active: false,
      };
      
      const scenario = await TestScenarioService.createScenario(scenarioData);
      
      expect(scenario.is_active).toBe(false);
      
      // Clean up
      await TestScenarioService.deleteScenario(scenario.id);
    });
  });

  describe('GET /scenarios/{id}', () => {
    it('should fetch a specific scenario by ID', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      const scenario = await TestScenarioService.getScenario(createdScenario.id);
      
      expect(scenario).toEqual(createdScenario);
    });

    it('should throw error for non-existent scenario', async () => {
      const nonExistentId = 99999;
      
      await expect(TestScenarioService.getScenario(nonExistentId)).rejects.toThrow();
    });
  });

  describe('PUT /scenarios/{id}', () => {
    it('should update a scenario', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      const updatedScenarioData = await TestScenarioService.updateScenario(
        createdScenario.id, 
        updatedScenario
      );
      
      expect(updatedScenarioData.id).toBe(createdScenario.id);
      expect(updatedScenarioData.name).toBe(updatedScenario.name);
      expect(updatedScenarioData.is_active).toBe(updatedScenario.is_active);
      expect(updatedScenarioData.created_at).toBe(createdScenario.created_at);
      expect(updatedScenarioData.updated_at).not.toBe(createdScenario.updated_at);
      
      // Update the createdScenario reference for cleanup
      createdScenario = updatedScenarioData;
    });

    it('should update only the name field', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      const originalActive = createdScenario.is_active;
      const updateData: ScenarioUpdate = {
        name: 'Partial Update Test',
      };

      const updatedScenarioData = await TestScenarioService.updateScenario(
        createdScenario.id, 
        updateData
      );
      
      expect(updatedScenarioData.name).toBe(updateData.name);
      expect(updatedScenarioData.is_active).toBe(originalActive);
      
      // Update the createdScenario reference for cleanup
      createdScenario = updatedScenarioData;
    });

    it('should update only the is_active field', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      const originalName = createdScenario.name;
      const updateData: ScenarioUpdate = {
        is_active: true,
      };

      const updatedScenarioData = await TestScenarioService.updateScenario(
        createdScenario.id, 
        updateData
      );
      
      expect(updatedScenarioData.name).toBe(originalName);
      expect(updatedScenarioData.is_active).toBe(updateData.is_active);
      
      // Update the createdScenario reference for cleanup
      createdScenario = updatedScenarioData;
    });

    it('should throw error when updating non-existent scenario', async () => {
      const nonExistentId = 99999;
      
      await expect(
        TestScenarioService.updateScenario(nonExistentId, updatedScenario)
      ).rejects.toThrow();
    });
  });

  describe('DELETE /scenarios/{id}', () => {
    it('should delete a scenario', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      await expect(
        TestScenarioService.deleteScenario(createdScenario.id)
      ).resolves.not.toThrow();

      // Verify the scenario is deleted
      await expect(
        TestScenarioService.getScenario(createdScenario.id)
      ).rejects.toThrow();

      // Clear the reference since it's deleted
      createdScenario = null as any;
    });

    it('should throw error when deleting non-existent scenario', async () => {
      const nonExistentId = 99999;
      
      await expect(
        TestScenarioService.deleteScenario(nonExistentId)
      ).rejects.toThrow();
    });
  });

  describe('Scenario validation', () => {
    it('should reject scenario with empty name', async () => {
      const invalidScenario: ScenarioCreate = {
        name: '',
        difficulty: 'Normal',
        size: '10',
        is_active: true,
      };

      await expect(
        TestScenarioService.createScenario(invalidScenario)
      ).rejects.toThrow();
    });

    it('should reject scenario with whitespace-only name', async () => {
      const invalidScenario: ScenarioCreate = {
        name: '   ',
        difficulty: 'Normal',
        size: '10',
        is_active: true,
      };

      await expect(
        TestScenarioService.createScenario(invalidScenario)
      ).rejects.toThrow();
    });

    it('should reject scenario with name longer than 100 characters', async () => {
      const invalidScenario: ScenarioCreate = {
        name: 'a'.repeat(101),
        difficulty: 'Normal',
        size: '10',
        is_active: true,
      };

      await expect(
        TestScenarioService.createScenario(invalidScenario)
      ).rejects.toThrow();
    });
  });

  describe('Scenario uniqueness', () => {
    it('should reject duplicate scenario names', async () => {
      const scenarioData: ScenarioCreate = {
        name: 'Unique Test Scenario',
        difficulty: 'Normal',
        size: '10',
        is_active: true,
      };

      // Create first scenario
      const firstScenario = await TestScenarioService.createScenario(scenarioData);
      
      // Try to create second scenario with same name
      await expect(
        TestScenarioService.createScenario(scenarioData)
      ).rejects.toThrow();

      // Clean up
      await TestScenarioService.deleteScenario(firstScenario.id);
    });
  });
}); 