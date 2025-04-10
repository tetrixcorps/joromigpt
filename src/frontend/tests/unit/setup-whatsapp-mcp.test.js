// tests/unit/setup-whatsapp-mcp.test.js
// Add at the top of the file, after the mocks
// Mock process.exit
const originalExit = process.exit;
beforeAll(() => {
  process.exit = jest.fn();
});
afterAll(() => {
  process.exit = originalExit;
});

// Then in your tests, you can check if process.exit was called:
test('should exit if Node.js version is too low', () => {
  jest.resetModules();
  execSync.mockImplementation((cmd) => {
    if (cmd === 'node --version') {
      return 'v18.0.0'; // Lower version
    }
    return '';
  });
  
  require('../../scripts/setup-whatsapp-mcp');
  
  expect(process.exit).toHaveBeenCalledWith(1);
});