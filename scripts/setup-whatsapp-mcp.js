#!/usr/bin/env node
// /home/diegomartinez/Desktop/joromigpt/scripts/setup-whatsapp-mcp.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const homeDir = os.homedir();
const rootDir = '/home/diegomartinez/Desktop/joromigpt';
const repoPath = path.join(rootDir, 'whatsapp-mcp-ts');

// Check Node.js version
try {
  const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
  const versionMatch = nodeVersion.match(/v(\d+)\.(\d+)\.(\d+)/);
  
  if (versionMatch) {
    const [, major] = versionMatch;
    if (parseInt(major) < 23) {
      console.error('Error: Node.js version 23.10.0 or higher is required.');
      console.error(`Your version: ${nodeVersion}`);
      process.exit(1);
    }
  }
} catch (error) {
  console.error('Error checking Node.js version:', error.message);
  process.exit(1);
}

console.log('Setting up WhatsApp MCP server for African Voice AI...');

// Clone the repository if it doesn't exist
if (!fs.existsSync(repoPath)) {
  console.log('Cloning WhatsApp MCP repository...');
  execSync('git clone https://github.com/jlucaso1/whatsapp-mcp-ts.git', { cwd: rootDir });
}

// Install dependencies
console.log('Installing dependencies...');
execSync('npm install', { cwd: repoPath });

// Create data directory
const dataDir = path.join(repoPath, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Create auth_info directory
const authDir = path.join(repoPath, 'auth_info');
if (!fs.existsSync(authDir)) {
  fs.mkdirSync(authDir, { recursive: true });
}

// Create MCP configuration file for Claude Desktop
const askForClaudeDesktopConfig = () => {
  rl.question('Do you want to set up Claude Desktop configuration? (y/n): ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      // Check OS and adjust path
      let configPath;
      if (process.platform === 'darwin') {
        configPath = path.join(homeDir, 'Library', 'Application Support', 'Claude');
      } else if (process.platform === 'win32') {
        configPath = path.join(homeDir, 'AppData', 'Roaming', 'Claude');
      } else {
        configPath = path.join(homeDir, '.config', 'Claude');
      }
      
      // Create directory if it doesn't exist
      if (!fs.existsSync(configPath)) {
        fs.mkdirSync(configPath, { recursive: true });
      }
      
      // Create Claude Desktop config
      const claudeConfig = {
        "mcps": [
          {
            "name": "whatsapp",
            "command": ["node", "--no-warnings", path.join(repoPath, "src", "main.ts")],
            "cwd": repoPath
          }
        ]
      };
      
      fs.writeFileSync(
        path.join(configPath, 'claude_desktop_config.json'),
        JSON.stringify(claudeConfig, null, 2)
      );
      
      console.log(`Claude Desktop configuration created at: ${path.join(configPath, 'claude_desktop_config.json')}`);
      askForCursorConfig();
    } else {
      askForCursorConfig();
    }
  });
};

// Create MCP configuration file for Cursor
const askForCursorConfig = () => {
  rl.question('Do you want to set up Cursor configuration? (y/n): ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      const cursorConfigDir = path.join(homeDir, '.cursor');
      
      // Create directory if it doesn't exist
      if (!fs.existsSync(cursorConfigDir)) {
        fs.mkdirSync(cursorConfigDir, { recursive: true });
      }
      
      // Create Cursor config
      const cursorConfig = {
        "mcps": [
          {
            "name": "whatsapp",
            "command": ["node", "--no-warnings", path.join(repoPath, "src", "main.ts")],
            "cwd": repoPath
          }
        ]
      };
      
      fs.writeFileSync(
        path.join(cursorConfigDir, 'mcp.json'),
        JSON.stringify(cursorConfig, null, 2)
      );
      
      console.log(`Cursor configuration created at: ${path.join(cursorConfigDir, 'mcp.json')}`);
      askForAutostart();
    } else {
      askForAutostart();
    }
  });
};

// Ask if user wants to set up autostart
const askForAutostart = () => {
  rl.question('Do you want to set up automatic startup of the WhatsApp MCP server? (y/n): ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      setupAutostart();
    } else {
      finishSetup();
    }
  });
};

// Set up autostart using systemd (Linux only)
const setupAutostart = () => {
  if (process.platform !== 'linux') {
    console.log('Automatic startup is currently only supported on Linux systems.');
    finishSetup();
    return;
  }
  
  try {
    const serviceContent = `[Unit]
Description=WhatsApp MCP Server for African Voice AI
After=network.target

[Service]
ExecStart=/usr/bin/node --no-warnings ${path.join(repoPath, 'src', 'main.ts')}
WorkingDirectory=${repoPath}
Restart=always
User=${os.userInfo().username}
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
`;

    const serviceFilePath = path.join(homeDir, '.config', 'systemd', 'user', 'whatsapp-mcp.service');
    
    // Create directory if it doesn't exist
    const serviceDir = path.dirname(serviceFilePath);
    if (!fs.existsSync(serviceDir)) {
      fs.mkdirSync(serviceDir, { recursive: true });
    }
    
    fs.writeFileSync(serviceFilePath, serviceContent);
    
    console.log('Created systemd service file at:', serviceFilePath);
    console.log('To enable and start the service, run:');
    console.log('systemctl --user enable whatsapp-mcp.service');
    console.log('systemctl --user start whatsapp-mcp.service');
    
    finishSetup();
  } catch (error) {
    console.error('Failed to set up autostart:', error);
    finishSetup();
  }
};

// Final instructions
const finishSetup = () => {
  console.log('\nSetup complete!');
  console.log('\nTo start the WhatsApp MCP server manually:');
  console.log(`1. Navigate to: ${repoPath}`);
  console.log('2. Run: node --no-warnings src/main.ts');
  console.log('\nWhen you first connect, you will need to scan a QR code with your WhatsApp app.');
  console.log('The QR code will appear in the terminal or you can access it through the WhatsApp integration page in the app.');
  
  console.log('\nTroubleshooting:');
  console.log('- If you see experimental feature warnings, the --no-warnings flag is automatically applied');
  console.log('- For authentication issues, delete the auth_info directory and restart the server');
  console.log('- Check wa-logs.txt and mcp-logs.txt in the WhatsApp MCP directory for detailed logs');
  
  rl.close();
};

// Start the setup process
askForClaudeDesktopConfig();