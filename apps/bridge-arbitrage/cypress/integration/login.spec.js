describe('Login Page', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3001/login');
  });

  it('should display login form', () => {
    cy.get('[data-test-id="login-form-submit-button"]')
      .should('contain', 'Se connecter')
      .should('be.visible');

    cy.get('input[type="email"]')
      .should('be.visible');

    cy.get('input[type="password"]')
      .should('be.visible');
  });

  it('should show error message for invalid credentials', () => {
    cy.get('input[type="email"]').type('invalid@email.com');
    cy.get('input[type="password"]').type('wrongpassword');
    cy.get('[data-test-id="login-form-submit-button"]').click();

    cy.get('.tui-form__error')
      .should('be.visible')
      .should('contain', 'Invalid credentials');
  });

  it('should allow successful login', () => {
    cy.intercept('POST', '/auth/v1/token', {
      statusCode: 200,
      body: {
        access_token: 'test-token',
        expires_in: 3600,
        token_type: 'bearer'
      }
    }).as('loginRequest');

    cy.get('input[type="email"]').type('test@email.com');
    cy.get('input[type="password"]').type('testpassword');
    cy.get('[data-test-id="login-form-submit-button"]').click();

    cy.wait('@loginRequest');
    cy.url().should('not.include', '/login');
  });
});
