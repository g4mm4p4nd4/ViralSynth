import { test, expect } from '@playwright/test';

test('home page shows tabs', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await expect(page.locator('text=Trending Audio')).toBeVisible();
  await expect(page.locator('text=Patterns')).toBeVisible();
  await expect(page.locator('text=Generate')).toBeVisible();
});
