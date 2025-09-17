import { test, expect } from '@playwright/test';

const audioRoute = '**/api/audio/trending**';
const patternsRoute = '**/api/patterns**';
const generateRoute = '**/api/generate';

test('audio dashboard renders mocked rankings', async ({ page }) => {
  await page.route(audioRoute, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          audio_id: 'audio-1',
          audio_hash: 'hash-1',
          count: 12,
          avg_engagement: 45.5,
          url: 'https://example.com/audio-1',
          niche: 'tech',
        },
      ]),
    });
  });

  await page.goto('/dashboard/audio');
  await expect(page.getByRole('heading', { name: 'Trending Audio' })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'audio-1' })).toBeVisible();
});


test('patterns dashboard sorts and renders cards', async ({ page }) => {
  await page.route(patternsRoute, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 1,
          hook: 'Hook One',
          core_value_loop: 'Value',
          narrative_arc: 'Arc',
          visual_formula: 'Visual',
          cta: 'CTA',
          prevalence: 0.2,
          engagement_score: 0.5,
        },
        {
          id: 2,
          hook: 'Hook Two',
          core_value_loop: 'Value',
          narrative_arc: 'Arc',
          visual_formula: 'Visual',
          cta: 'CTA',
          prevalence: 0.8,
          engagement_score: 0.9,
        },
      ]),
    });
  });

  await page.goto('/dashboard/patterns');
  await expect(page.getByRole('heading', { name: 'Pattern Insights' })).toBeVisible();
  await expect(page.getByText('Hook Two')).toBeVisible();
});


test('generate dashboard displays response with explanation', async ({ page }) => {
  await page.route(generateRoute, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        script: 'Test script',
        storyboard: ['https://example.com/frame-1'],
        notes: ['Note one'],
        variations: {
          tiktok: { hook: 'TikTok Hook', cta: 'TikTok CTA' },
        },
        why: {
          pattern: {
            pattern_id: 1,
            hook: 'Hook',
            prevalence: 0.5,
            engagement_score: 0.7,
            score: 0.6,
            explanation: 'Most balanced pattern',
          },
          audio: {
            audio_id: 'audio-1',
            usage_count: 10,
            avg_engagement: 75,
            score: 45,
            explanation: 'High engagement audio',
          },
        },
      }),
    });
  });

  await page.goto('/dashboard/generate');
  await page.fill('textarea', 'Testing generation');
  await page.click('button:has-text("Generate Package")');

  await expect(page.getByRole('heading', { name: 'Why these choices?' })).toBeVisible();
  await expect(page.getByText('High engagement audio')).toBeVisible();
});
