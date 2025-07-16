/// <reference types="cypress" />

describe('Login Page', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should display the login form', () => {
    cy.get('h1').should('contain', 'GuildRoster');
    cy.get('p').should('contain', 'Sign in to your account');
    cy.get('input[name="username"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('contain', 'Sign in');
  });

  it('should allow user to enter credentials', () => {
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('testpass');
    
    cy.get('input[name="username"]').should('have.value', 'testuser');
    cy.get('input[name="password"]').should('have.value', 'testpass');
  });

  it('should show loading state when form is submitted', () => {
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('testpass');
    cy.get('button[type="submit"]').click();
    
    cy.get('button[type="submit"]').should('contain', 'Signing in...');
    cy.get('button[type="submit"]').should('be.disabled');
  });

  it('should have proper form validation', () => {
    // Try to submit without filling required fields
    cy.get('button[type="submit"]').click();
    
    // Form should still be visible (not submitted)
    cy.get('form').should('be.visible');
  });

  it('should have accessible form elements', () => {
    cy.get('input[name="username"]').should('have.attr', 'id', 'username');
    cy.get('input[name="password"]').should('have.attr', 'id', 'password');
    cy.get('input[name="username"]').should('have.attr', 'required');
    cy.get('input[name="password"]').should('have.attr', 'required');
  });

  it('should have remember me checkbox', () => {
    cy.get('input[type="checkbox"]').should('be.visible');
    cy.get('label').should('contain', 'Remember me');
  });



  it('should navigate back to home when clicking logo', () => {
    cy.get('h1').click();
    cy.url().should('eq', Cypress.config().baseUrl + '/');
  });
}); 