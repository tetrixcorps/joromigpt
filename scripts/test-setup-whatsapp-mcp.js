// scripts/test-setup-whatsapp-mcp.js
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');
const fs = require('fs');

const testDir = path.join(os.tmpdir(), 'whatsapp-mcp-test-' + Date.now());
console.log(`Creating test environment in: ${testDir}`);

// Create test directory
fs.mkdirSync(testDir, { recursive: true });

// Copy setup script to test directory
const originalScript = path.join(__dirname, 'setup-whatsapp-mcp.js');
const testScript = path.join(testDir, 'setup-whatsapp-mcp.js');

// Read original script
let scriptContent = fs.readFileSync(originalScript, 'utf8');

// Modify paths to use test directory
scriptContent = scriptContent.replace(
  "const rootDir = '/home/diegomartinez/Desktop/joromigpt';",
  `const rootDir = '${testDir}';`
);

// Add a dry-run flag for potentially destructive operations
scriptContent = scriptContent.replace(
  /execSync\('git clone (.*?)'\)/g,
  "console.log('[DRY RUN] Would execute: git clone $1')"
);

// Save modified script
fs.writeFileSync(testScript, scriptContent);
console.log(`Created test script at: ${testScript}`);

// Make it executable
fs.chmodSync(testScript, '755');

console.log('\nTo run the test script:');
console.log(`node ${testScript}`);
console.log('\nAfter testing, you can delete the test directory:');
console.log(`rm -rf "${testDir}"`);