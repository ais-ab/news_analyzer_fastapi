import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.click('button:has-text("Sign In")');
    await expect(page).toHaveURL('/');
  });

  test('should display dashboard with statistics', async ({ page }) => {
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=Welcome to your personalized news analysis dashboard')).toBeVisible();
  });

  test('should navigate to business interest page', async ({ page }) => {
    await page.click('text=Set Business Interest');
    await expect(page).toHaveURL('/business-interest');
    await expect(page.locator('text=Business Interest')).toBeVisible();
  });

  test('should navigate to sources page', async ({ page }) => {
    await page.click('text=Manage Sources');
    await expect(page).toHaveURL('/sources');
    await expect(page.locator('text=News Sources')).toBeVisible();
  });

  test('should navigate to analysis page', async ({ page }) => {
    await page.click('text=Run Analysis');
    await expect(page).toHaveURL('/analysis');
    await expect(page.locator('text=News Analysis')).toBeVisible();
  });

  test('should display quick actions', async ({ page }) => {
    await expect(page.locator('text=Quick Actions')).toBeVisible();
    await expect(page.locator('text=Set Business Interest')).toBeVisible();
    await expect(page.locator('text=Manage Sources')).toBeVisible();
    await expect(page.locator('text=Run Analysis')).toBeVisible();
  });
}); 