import { expect, test, type Page } from '@playwright/test';

const hostname = "http://localhost:8080"

// run add.py

async function inputCredentialsAndLogin(page: Page, email: string, password: string)
{
    await page.getByRole('textbox', { name: 'Email' }).fill(email);
    await page.getByRole('textbox', { name: 'Password' }).fill(password);
    await page.getByRole('button', { name: 'Log In' }).click();
}


test('loginUser', async ({ page }) => {
    await page.goto(`${hostname}/login`);
    await page.waitForTimeout(1000);
    await expect(page.getByRole('radio', { name: 'User' })).toHaveAttribute('aria-checked', 'true');
    await expect(page.locator('main')).not.toContainClass('dark');
    await inputCredentialsAndLogin(page, 'user@example.com', 'user123')
    await expect(page).toHaveURL(`${hostname}/dashboard`);
    await expect(page.getByRole('heading', { name: 'My Page'})).toBeVisible();
});


test('loginAdmin', async ({ page }) => {
    await page.goto(`${hostname}/login`);
    await page.waitForTimeout(1000);
    await page.getByRole('radio', { name: 'Admin' }).click();
    await expect(page.getByRole('radio', { name: 'Admin' })).toHaveAttribute('aria-checked', 'true');
    await expect(page.locator('main')).toContainClass('dark');
    await inputCredentialsAndLogin(page, 'admin@example.com', 'admin123');
    await expect(page).toHaveURL(`${hostname}/admin/dashboard`);
    await expect(page.getByRole('button', { name: 'Add user' })).toBeVisible();
});


test('logoutUser', async ({ page }) => {
    await page.goto(`${hostname}/login`);
    await page.waitForTimeout(1000);
    await inputCredentialsAndLogin(page, 'user@example.com', 'user123');
    await expect(page).toHaveURL(`${hostname}/dashboard`);
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
    await page.getByRole('button', { name: 'Logout' }).click();
    await expect(page).toHaveURL(`${hostname}/login`);
    const response = await page.request.get(`${hostname}/api/user/me`);
    expect(response.status()).toBe(401);
});


test('loginFail', async ({ page }) => {
    await page.goto(`${hostname}/login`);
    await page.waitForTimeout(1000);
    await inputCredentialsAndLogin(page, 'nouser@example.com', '67');
    await expect(page).toHaveURL(`${hostname}/login`);
    await expect(page.getByText('Invalid email or password')).toBeVisible();
});


test('loginUserAsAdmin', async ({ page }) => {
    await page.goto(`${hostname}/login`);
    await page.waitForTimeout(1000);
    await page.getByRole('radio', { name: 'Admin' }).click();
    await inputCredentialsAndLogin(page, 'user@example.com', 'user123');
    await expect(page).toHaveURL(`${hostname}/login`);
    await expect(page.getByText('Admin access required')).toBeVisible();
    const response = await page.request.get(`${hostname}/api/user/me`);
    expect(response.status()).toBe(401);
});


test('unathenticatedAccess', async ({ page }) => {
    await page.goto(`${hostname}/dashboard`);
    await expect(page.getByText('Authenticating')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'My Page'})).not.toBeVisible();
    await expect(page).toHaveURL(`${hostname}/login`);
    const response = await page.request.get(`${hostname}/api/user/me`);
    expect(response.status()).toBe(401);    
});

test('unauthorisedAccess', async ({ page }) => {
    await page.goto(`${hostname}/login`);
    await page.waitForTimeout(1000);
    await inputCredentialsAndLogin(page, 'user@example.com', 'user123');
    await expect(page).toHaveURL(`${hostname}/dashboard`);
    await page.goto(`${hostname}/admin/dashboard`);
    await expect(page.getByRole('button', { name: 'Add user' })).not.toBeVisible();
    await expect(page).toHaveURL(`${hostname}/dashboard`);
});

