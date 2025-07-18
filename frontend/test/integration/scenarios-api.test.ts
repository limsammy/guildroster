import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { ScenarioService } from '../../app/api/scenarios';
import type { Scenario, ScenarioCreate, ScenarioUpdate } from '../../app/api/types';

// Test data
const testScenario: ScenarioCreate = {
  name: 'Test Scenario',
  is_active: true,
};

const updatedScenario: ScenarioUpdate = {
  name: 'Updated Test Scenario',
  is_active: false,
};

describe('Scenarios API Integration Tests', () => {
  let createdScenario: Scenario;

  beforeAll(async () => {
    // Ensure we have a clean state by deleting any test scenarios
    try {
      const scenarios = await ScenarioService.getScenarios();
      const testScenarios = scenarios.filter(s => 
        s.name.includes('Test Scenario') || s.name.includes('Updated Test Scenario')
      );
      for (const scenario of testScenarios) {
        await ScenarioService.deleteScenario(scenario.id);
      }
    } catch (error) {
      // Ignore errors during cleanup
    }
  });

  afterAll(async () => {
    // Clean up test data
    try {
      if (createdScenario) {
        await ScenarioService.deleteScenario(createdScenario.id);
      }
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('GET /scenarios/', () => {
    it('should fetch all scenarios', async () => {
      const scenarios = await ScenarioService.getScenarios();
      
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
      const activeScenarios = await ScenarioService.getActiveScenarios();
      
      expect(Array.isArray(activeScenarios)).toBe(true);
      activeScenarios.forEach(scenario => {
        expect(scenario.is_active).toBe(true);
      });
    });
  });

  describe('POST /scenarios/', () => {
    it('should create a new scenario', async () => {
      createdScenario = await ScenarioService.createScenario(testScenario);
      
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
      };
      
      const scenario = await ScenarioService.createScenario(scenarioData);
      
      expect(scenario.is_active).toBe(true);
      
      // Clean up
      await ScenarioService.deleteScenario(scenario.id);
    });

    it('should create an inactive scenario', async () => {
      const scenarioData: ScenarioCreate = {
        name: 'Test Scenario Inactive',
        is_active: false,
      };
      
      const scenario = await ScenarioService.createScenario(scenarioData);
      
      expect(scenario.is_active).toBe(false);
      
      // Clean up
      await ScenarioService.deleteScenario(scenario.id);
    });
  });

  describe('GET /scenarios/{id}', () => {
    it('should fetch a specific scenario by ID', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      const scenario = await ScenarioService.getScenario(createdScenario.id);
      
      expect(scenario).toEqual(createdScenario);
    });

    it('should throw error for non-existent scenario', async () => {
      const nonExistentId = 99999;
      
      await expect(ScenarioService.getScenario(nonExistentId)).rejects.toThrow();
    });
  });

  describe('PUT /scenarios/{id}', () => {
    it('should update a scenario', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      const updatedScenarioData = await ScenarioService.updateScenario(
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

      const updatedScenarioData = await ScenarioService.updateScenario(
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

      const updatedScenarioData = await ScenarioService.updateScenario(
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
        ScenarioService.updateScenario(nonExistentId, updatedScenario)
      ).rejects.toThrow();
    });
  });

  describe('DELETE /scenarios/{id}', () => {
    it('should delete a scenario', async () => {
      if (!createdScenario) {
        throw new Error('No scenario created for testing');
      }

      await expect(
        ScenarioService.deleteScenario(createdScenario.id)
      ).resolves.not.toThrow();

      // Verify the scenario is deleted
      await expect(
        ScenarioService.getScenario(createdScenario.id)
      ).rejects.toThrow();

      // Clear the reference since it's deleted
      createdScenario = null as any;
    });

    it('should throw error when deleting non-existent scenario', async () => {
      const nonExistentId = 99999;
      
      await expect(
        ScenarioService.deleteScenario(nonExistentId)
      ).rejects.toThrow();
    });
  });

  describe('Scenario validation', () => {
    it('should reject scenario with empty name', async () => {
      const invalidScenario: ScenarioCreate = {
        name: '',
        is_active: true,
      };

      await expect(
        ScenarioService.createScenario(invalidScenario)
      ).rejects.toThrow();
    });

    it('should reject scenario with whitespace-only name', async () => {
      const invalidScenario: ScenarioCreate = {
        name: '   ',
        is_active: true,
      };

      await expect(
        ScenarioService.createScenario(invalidScenario)
      ).rejects.toThrow();
    });

    it('should reject scenario with name longer than 100 characters', async () => {
      const invalidScenario: ScenarioCreate = {
        name: 'a'.repeat(101),
        is_active: true,
      };

      await expect(
        ScenarioService.createScenario(invalidScenario)
      ).rejects.toThrow();
    });
  });

  describe('Scenario uniqueness', () => {
    it('should reject duplicate scenario names', async () => {
      const scenarioData: ScenarioCreate = {
        name: 'Unique Test Scenario',
        is_active: true,
      };

      // Create first scenario
      const firstScenario = await ScenarioService.createScenario(scenarioData);
      
      // Try to create second scenario with same name
      await expect(
        ScenarioService.createScenario(scenarioData)
      ).rejects.toThrow();

      // Clean up
      await ScenarioService.deleteScenario(firstScenario.id);
    });
  });
}); 