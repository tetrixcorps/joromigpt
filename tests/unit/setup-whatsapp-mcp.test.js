// tests/unit/setup-whatsapp-mcp.test.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

// Mock child_process
jest.mock('child_process', () => ({
  execSync: jest.fn()
}));

// Mock process.exit
const originalExit = process.exit;
beforeAll(() => {
  process.exit = jest.fn();
});
afterAll(() => {
  process.exit = originalExit;
});

// Mock dependencies
jest.mock('fs');

// Other test setup code...

describe('WhatsApp MCP Setup Script', () => {
  let originalProcessPlatform;
  const mockHomeDir = '/mock/home';
  const mockRootDir = '/mock/home/Desktop/joromigpt';
  const mockRepoPath = '/mock/home/Desktop/joromigpt/whatsapp-mcp-ts';
  
  beforeEach(() => {
    // Save original platform and mock it
    originalProcessPlatform = process.platform;
    Object.defineProperty(process, 'platform', { value: 'linux' });
    
    // Mock os.homedir
    os.homedir = jest.fn().mockReturnValue(mockHomeDir);
    os.userInfo = jest.fn().mockReturnValue({ username: 'testuser' });
    
    // Mock execSync
    execSync.mockImplementation((cmd) => {
      if (cmd === 'node --version') {
        return 'v23.10.0';
      }
      return '';
    });
    
    // Mock fs functions
    fs.existsSync.mockImplementation((path) => false);
    fs.mkdirSync.mockImplementation(() => undefined);
    fs.writeFileSync.mockImplementation(() => undefined);
    
    // Reset mocks
    jest.clearAllMocks();
  });
  
  afterEach(() => {
    // Restore original platform
    Object.defineProperty(process, 'platform', { value: originalProcessPlatform });
  });
  
  test('should check Node.js version', () => {
    // Reset module registry to run script again
    jest.resetModules();
    
    // Run the script
    require('../../scripts/setup-whatsapp-mcp');
    
    // Verify execSync was called with the right command
    expect(execSync).toHaveBeenCalledWith('node --version', { encoding: 'utf8' });
  });
  
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
  
  test('should clone the repository if it does not exist', () => {
    jest.resetModules();
    
    require('../../scripts/setup-whatsapp-mcp');
    
    expect(fs.existsSync).toHaveBeenCalledWith(mockRepoPath);
    expect(execSync).toHaveBeenCalledWith(
      'git clone https://github.com/jlucaso1/whatsapp-mcp-ts.git',
      { cwd: mockRootDir }
    );
  });
  
  // Additional tests...
});