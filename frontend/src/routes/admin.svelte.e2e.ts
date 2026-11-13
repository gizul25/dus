import { expect, test, type Page } from '@playwright/test';

// change to "http://localhost:8080" if running not from docker.
// const hostname = "http://localhost:8080"
const hostname = "http://nginx:8080"

async function loginAsAdmin(page: Page) {
    await page.goto(`${hostname}/login`);
    await page.waitForTimeout(3000);
    await page.getByRole('radio', { name: 'Admin' }).click();
    await page.getByRole('textbox', { name: 'Email' }).click();
    await page.getByRole('textbox', { name: 'Email' }).fill('admin@example.com');
    await page.getByRole('textbox', { name: 'Password' }).click();
    await page.getByRole('textbox', { name: 'Password' }).fill('admin123');
    await page.getByRole('button', { name: 'Log In' }).click();
}

async function switchToDeskTab(page: Page) {
    // If you try to switch while page is loading, the tab button will not work as expected.
    await page.waitForTimeout(3000);
    await page.getByRole('tab', { name: 'Desks' }).click();
    await expect(page.getByRole('button', { name: 'Add desk' })).toBeVisible();
}

test('createUser', async ({ page }) => {
    await loginAsAdmin(page);
    await expect(page.getByRole('button', { name: 'Add user' })).toBeVisible();
    await page.getByRole('button', { name: 'Add user' }).click();
    await page.getByRole('textbox', { name: 'First name' }).click();
    await page.getByRole('textbox', { name: 'First name' }).fill('TestName');
    await page.getByRole('textbox', { name: 'First name' }).press('Tab');
    await page.getByRole('textbox', { name: 'Last name' }).fill('LastName');
    await page.getByRole('textbox', { name: 'Email', exact: true }).click();
    await page.getByRole('textbox', { name: 'Email', exact: true }).fill('test@example.com');
    await page.getByRole('textbox', { name: 'Password' }).click();
    await page.getByRole('textbox', { name: 'Password' }).fill('password123');
    await page.getByRole('button', { name: 'Create new user' }).click();
    await expect(page.getByRole('cell', { name: 'TestName' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'LastName' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'test@example.com' })).toBeVisible();
});

test('editUser', async ({ page }) => {
    await loginAsAdmin(page);
    await expect(page.getByRole('button', { name: 'Add user' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'TestName' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'LastName' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'test@example.com' })).toBeVisible();
    await page.getByRole('row', { name: 'Select row TestName LastName' }).getByLabel('Edit button').click();
    await page.getByRole('textbox', { name: 'First name' }).click();
    await page.getByRole('textbox', { name: 'First name' }).fill('TestName_changed');
    await page.getByRole('textbox', { name: 'Last name' }).click();
    await page.getByRole('textbox', { name: 'Last name' }).fill('LastName_changed');
    await page.getByRole('button', { name: 'Edit user' }).click();
    await expect(page.getByRole('cell', { name: 'TestName_changed' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'LastName_changed' })).toBeVisible();
});

test('deleteUser', async ({ page }) => {
    await loginAsAdmin(page);
    await expect(page.getByRole('cell', { name: 'TestName_changed' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'LastName_changed' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'test@example.com' })).toBeVisible();
    await page.getByRole('row', { name: 'Select row TestName_changed LastName_changed' }).getByLabel('Actions menu button').click();
    await page.getByRole('menuitem', { name: 'Delete user' }).click();
    await page.getByRole('button', { name: 'Continue' }).click();
    await expect(page.getByRole('cell', { name: 'TestName_changed' })).toHaveCount(0);
});

test('createDesk', async ({ page }) => {
    await loginAsAdmin(page);
    await switchToDeskTab(page);
    await expect(page.getByRole('cell', { name: 'No results.' })).toBeVisible();
    await page.getByRole('button', { name: 'Add desk' }).click();
    await page.getByRole('textbox', { name: 'Name' }).fill('testdesk');
    await page.getByRole('button', { name: 'Create new desk' }).click();
    await expect(page.getByRole('cell', { name: 'testdesk' })).toBeVisible();
});

test('editDesk', async ({ page }) => {
    await loginAsAdmin(page);
    await switchToDeskTab(page);
    await expect(page.getByRole('cell', { name: 'testdesk' })).toBeVisible();
    await page.getByRole('button', { name: 'Edit button' }).click();
    await page.getByRole('textbox', { name: 'Name' }).click();
    await page.getByRole('textbox', { name: 'Name' }).fill('testdesk_changed');
    await page.getByRole('button', { name: 'Edit desk' }).click();
    await expect(page.getByRole('cell', { name: 'testdesk_changed' })).toBeVisible();
});

test('deleteDesk', async ({ page }) => {
    await loginAsAdmin(page);
    await switchToDeskTab(page);
    await expect(page.getByRole('cell', { name: 'testdesk_changed' })).toBeVisible();
    await page.getByRole('button', { name: 'Actions menu button' }).click();
    await page.getByRole('menuitem', { name: 'Delete desk' }).click();
    await page.getByRole('button', { name: 'Continue' }).click();
    await expect(page.getByRole('cell', { name: 'No results.' })).toBeVisible();
});