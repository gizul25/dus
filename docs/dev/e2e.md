# Playwright

- It often says that you're missing host dependencies to run browsers, but the list is too large. Even in a VM, which is running Linux Mint where I am already running a working browser, it lists many host dependencies which are missing.
- You can record your usage of the browser, and create tests that way: https://playwright.dev/docs/codegen-intro. Though, it requires running playwright in a system which supports seeing browser graphically. Not sure if WSL is supported. In any case, you can write tests manually or create a basic `pnpm` project with playwright dependency on your host, and then you'll have creating tests from your interaction functionality. I something something remember that maaybe you can also have playwright recorder as standalone app or browser extension, but I haven't looked into it.
    - Then, for example, it's just `pnpm playwright codegen http://localhost:8080/admin/dashboard`.
    - When copying test code, don't forget to put: `await page.goto('http://localhost:8080/admin/dashboard');`. Of course, change URL to tested page.
    - Also, you might need to change locators generated from codegen to be more accurate.
- For now, test are dependent to each other and expect to run on a fresh database.

Install dependencies:
```bash
# Full installation
pnpm playwright install
# For smaller no GUI version in Docker
pnpm playwright install --with-deps --only-shell chromium
```

Running tests (server needs to be running for E2E tests, running command doesn't launch server automatically):
```bash
pnpm test:e2e

# Preview them live
pnpm playwright test --ui
```

