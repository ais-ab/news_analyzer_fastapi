import { test, expect } from '@playwright/test';

test('basic app test', async ({ page }) => {
  // Just check if the app loads
  await page.goto('/');
  
  // Should redirect to login if not authenticated
  await expect(page).toHaveURL('/login');
  
  // Check if login form is visible
  await expect(page.locator('input[name="username"]')).toBeVisible();
  await expect(page.locator('input[name="password"]')).toBeVisible();
  
  console.log('Basic app test passed - login page loads correctly');
}); 