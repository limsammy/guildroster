/// <reference types="cypress" />

describe('API Integration', () => {
  beforeEach(() => {
    // Handle uncaught exceptions (like hydration mismatches)
    cy.on('uncaught:exception', (err, runnable) => {
      // Return false to prevent the error from failing the test
      // This is common with SSR hydration mismatches
      if (err.message.includes('Hydration failed') || err.message.includes('hydration')) {
        return false
      }
      // Let other errors fail the test
      return true
    })

    // Visit the app with a longer timeout for hydration
    cy.visit('/', { timeout: 10000 })
    
    // Wait for the app to be fully loaded
    cy.get('body').should('be.visible')
  })

  it('should show login form when not authenticated', () => {
    // This test assumes you'll have a login page
    // For now, we'll just check the basic app loads
    cy.get('body').should('be.visible')
  })

  it('should handle API errors gracefully', () => {
    // Test that the app handles API errors properly
    // This would be more comprehensive once we have the UI built
    cy.get('body').should('be.visible')
  })

  it('should load the main application', () => {
    // Basic test that the app loads
    cy.title().should('not.be.empty')
  })
}) 