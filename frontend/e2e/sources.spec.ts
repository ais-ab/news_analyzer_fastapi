import { test, expect } from '@playwright/test';

test.describe('Sources Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.click('button:has-text("Sign In")');
    await expect(page).toHaveURL('/');
    
    // Navigate to sources page
    await page.click('text=Manage Sources');
    await expect(page).toHaveURL('/sources');
  });

  test('should display sources page', async ({ page }) => {
    await expect(page.locator('text=News Sources')).toBeVisible();
    await expect(page.locator('text=Add New Source')).toBeVisible();
  });

  test('should add a new source', async ({ page }) => {
    // Fill in source URL
    await page.fill('input[placeholder="https://example.com"]', 'https://example.com/rss');
    
    // Click add button
    await page.click('button:has-text("Add Source")');
    
    // Wait for either success or error message
    await expect(page.locator('text=Source added successfully!')).toBeVisible({ timeout: 10000 });
  });

  test('should show validation error for invalid URL', async ({ page }) => {
    // Fill in invalid URL
    await page.fill('input[placeholder="https://example.com"]', 'invalid-url');
    
    // Click add button
    await page.click('button:has-text("Add Source")');
    
    // Should show validation error
    await expect(page.locator('text=Please enter a valid URL')).toBeVisible();
  });

  test('should display current sources', async ({ page }) => {
    await expect(page.locator('text=Your Sources')).toBeVisible();
  });

  test('should display popular sources', async ({ page }) => {
    await expect(page.locator('text=Popular Sources')).toBeVisible();
  });

  test('should remove a source', async ({ page }) => {
    // First add a source
    await page.fill('input[placeholder="https://example.com"]', 'https://example.com/rss');
    await page.click('button:has-text("Add Source")');
    
    // Wait for success message
    await expect(page.locator('text=Source added successfully!')).toBeVisible({ timeout: 10000 });
    
    // Then remove it by clicking the trash icon
    await page.click('button[title="Remove source"]');
    
    // Should show success message
    await expect(page.locator('text=Source removed successfully!')).toBeVisible({ timeout: 10000 });
  });

  test('should add popular source', async ({ page }) => {
    // Click on a popular source button (first one available)
    await page.click('button:has-text("Add")');
    
    // Should show success message
    await expect(page.locator('text=Source added successfully!')).toBeVisible({ timeout: 10000 });
  });
}); 