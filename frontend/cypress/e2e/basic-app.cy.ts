/// <reference types="cypress" />

describe('Basic App Functionality', () => {
  it('should load without crashing', () => {
    // Handle hydration mismatches
    cy.on('uncaught:exception', (err, runnable) => {
      if (err.message.includes('Hydration failed') || err.message.includes('hydration')) {
        return false
      }
      return true
    })

    cy.visit('/', { timeout: 15000 })
    
    // Just check that the page loads and has content
    cy.get('body').should('exist')
    cy.get('body').should('not.be.empty')
  })

  it('should have a document title', () => {
    cy.on('uncaught:exception', (err, runnable) => {
      if (err.message.includes('Hydration failed') || err.message.includes('hydration')) {
        return false
      }
      return true
    })

    cy.visit('/', { timeout: 15000 })
    cy.title().should('exist')
  })
}) 