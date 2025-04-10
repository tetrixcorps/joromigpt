// jest.setup.js
// Mock process.exit to prevent tests from terminating
const originalExit = process.exit;
process.exit = (code) => {
  console.error(`Test tried to call process.exit(${code})`);
  // Instead of exiting, throw an error that Jest can catch
  throw new Error(`process.exit(${code}) called`);
};

// Restore original process.exit after tests
afterAll(() => {
  process.exit = originalExit;
});