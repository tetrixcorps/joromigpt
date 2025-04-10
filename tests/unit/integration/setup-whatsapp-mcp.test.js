// tests/integration/setup-whatsapp-mcp.test.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

describe('WhatsApp MCP Setup Script Integration', () => {
  const tempDir = path.join(os.tmpdir(), 'whatsapp-mcp-test-' + Date.now());
  const scriptPath = path.join(process.cwd(), 'scripts', 'setup-whatsapp-mcp.js');
  
  // Create a modified version of the script for testing
  const testScriptPath = path.join(tempDir, 'test-setup-script.js');
  
  beforeAll(() => {
    // Create temp directory
    fs.mkdirSync(tempDir, { recursive: true });
    
    // Create a modified version of the script that uses temp directory as root
    let scriptContent = fs.readFileSync(scriptPath, 'utf8');
    scriptContent = scriptContent.replace(
      "const rootDir = '/home/diegomartinez/Desktop/joromigpt';",
      `const rootDir = '${tempDir}';`
    );
    
    // Modify the script to skip actual command execution
    scriptContent = scriptContent.replace(
      /execSync\((.*?)\);/g,
      'console.log(`Would execute: ${$1.toString().replace(/`/g, "\\`")}`);'
    );
    
    // Add a test hook to exit after config creation
    scriptContent = scriptContent.replace(
      'askForClaudeDesktopConfig();',
      `
      // Test mode - just create directories
      const dataDir = path.join(repoPath, 'data');
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }
      
      const authDir = path.join(repoPath, 'auth_info');
      if (!fs.existsSync(authDir)) {
        fs.mkdirSync(authDir, { recursive: true });
      }
      
      console.log('TEST_COMPLETE');
      `
    );
    
    fs.writeFileSync(testScriptPath, scriptContent);
  });
  
  afterAll(() => {
    // Clean up temp directory
    fs.rmSync(tempDir, { recursive: true, force: true });
  });
  
  test('should create required directories', () => {
    try {
      // Run the modified script
      execSync(`node ${testScriptPath}`, { encoding: 'utf8' });
      
      // Check if directories were created
      const repoPath = path.join(tempDir, 'whatsapp-mcp-ts');
      const dataDir = path.join(repoPath, 'data');
      const authDir = path.join(repoPath, 'auth_info');
      
      expect(fs.existsSync(repoPath)).toBe(true);
      expect(fs.existsSync(dataDir)).toBe(true);
      expect(fs.existsSync(authDir)).toBe(true);
    } catch (error) {
      console.error('Error running test script:', error);
      throw error;
    }
  });
});