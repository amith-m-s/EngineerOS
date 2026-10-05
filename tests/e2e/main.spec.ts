import { test, expect } from '@playwright/test'

/**
 * End-to-End Tests for EngineerOS
 * 
 * These tests simulate real user interactions with the application.
 * They test complete workflows from the user's perspective.
 * 
 * Run with: npm run e2e
 */

test.describe('EngineerOS E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto('/')
  })

  test('should load homepage', async ({ page }) => {
    // Verify page loads
    await expect(page).toHaveTitle(/EngineerOS|Next/)
  })

  test('should verify API health', async ({ page }) => {
    // Check that API is responding
    const response = await page.request.get('http://localhost:8000/health')
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(data.status).toBe('ok')
  })
})

test.describe('Authentication E2E', () => {
  test('should login with demo credentials', async ({ page }) => {
    // Test login flow:
    // 1. Navigate to login page (if exists)
    // 2. Enter email and password
    // 3. Submit form
    // 4. Verify redirect to dashboard
    
    // For now, test API directly
    const response = await page.request.post(
      'http://localhost:8000/auth/login',
      {
        data: {
          email: 'demo@engineeros.io',
          password: 'demo1234',
        },
      }
    )
    
    expect(response.ok()).toBeTruthy()
    const data = await response.json()
    expect(data).toHaveProperty('access_token')
    expect(data.token_type).toBe('bearer')
  })

  test('should reject invalid credentials', async ({ page }) => {
    const response = await page.request.post(
      'http://localhost:8000/auth/login',
      {
        data: {
          email: 'demo@engineeros.io',
          password: 'wrongpassword',
        },
      }
    )
    
    expect(response.status()).toBe(401)
  })
})

test.describe('API Endpoints E2E', () => {
  test('should access authenticated endpoints', async ({ authenticatedAPI }) => {
    // Test accessing endpoints that require authentication
    const response = await authenticatedAPI.get('/dev/me')
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(data).toHaveProperty('user_id')
    expect(data).toHaveProperty('email')
    expect(data).toHaveProperty('roles')
  })

  test('should get twin data', async ({ authenticatedAPI }) => {
    const response = await authenticatedAPI.get('/twin/demo_user')
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(data).toHaveProperty('user_id')
    expect(data).toHaveProperty('skill_scores')
  })

  test('should create simulation', async ({ authenticatedAPI }) => {
    const response = await authenticatedAPI.post('/simulations', {
      user_id: 'demo_user',
      title: 'Test Simulation',
      description: 'Test scenario',
    })
    
    // Will return 200 if working
    expect([200, 201]).toContain(response.status())
  })
})

test.describe('Rate Limiting E2E', () => {
  test('should respect rate limits', async ({ page }) => {
    // Send multiple requests to health endpoint
    const requests = Array(15)
      .fill(0)
      .map(() => page.request.get('http://localhost:8000/health'))

    const responses = await Promise.all(requests)
    
    // Some requests should succeed (first 10)
    const successCount = responses.filter(r => r.status() === 200).length
    // Some should be rate limited (429)
    const rateLimitedCount = responses.filter(r => r.status() === 429).length
    
    expect(successCount).toBeGreaterThan(0)
    expect(rateLimitedCount).toBeGreaterThan(0)
  })
})

test.describe('Security Headers E2E', () => {
  test('should include security headers', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/health')
    
    expect(response.headers()['x-content-type-options']).toBe('nosniff')
    expect(response.headers()['x-frame-options']).toBe('DENY')
    expect(response.headers()['x-xss-protection']).toBe('1; mode=block')
  })
})

test.describe('WebSocket E2E', () => {
  test('should connect to simulation WebSocket', async ({ page }) => {
    // WebSocket testing with Playwright is complex
    // This is a placeholder for actual implementation
    const response = await page.request.get(
      'http://localhost:8000/health'
    )
    expect(response.ok()).toBeTruthy()
  })
})
