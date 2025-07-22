/// <reference types="cypress" />

describe('App Loading', () => {
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
  })

  it('should load the application', () => {
    cy.visit('/', { timeout: 10000 })
    cy.get('body').should('be.visible')
  })

  it('should have a title', () => {
    cy.visit('/', { timeout: 10000 })
    cy.title().should('not.be.empty')
  })

  it('should show the welcome page', () => {
    cy.visit('/', { timeout: 10000 })
    // The React Router template should show some content
    // Wait a bit for hydration to complete
    cy.wait(1000)
    cy.get('body').should('contain.text', 'React Router')
  })
}) 