#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function runCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: true,
      ...options,
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

async function setupTests() {
  log('🚀 Setting up Frontend Testing Environment', 'bright');
  log('==========================================\n', 'bright');

  try {
    // Check if we're in the frontend directory
    if (!fs.existsSync('package.json')) {
      log('❌ Error: Please run this script from the frontend directory', 'red');
      process.exit(1);
    }

    log('📦 Installing dependencies...', 'cyan');
    await runCommand('npm', ['install']);
    log('✅ Dependencies installed successfully!', 'green');

    log('\n🎭 Installing Playwright browsers...', 'cyan');
    await runCommand('npx', ['playwright', 'install']);
    log('✅ Playwright browsers installed successfully!', 'green');

    log('\n🧪 Running initial unit tests...', 'cyan');
    try {
      await runCommand('npm', ['run', 'test:coverage']);
      log('✅ Unit tests are working!', 'green');
    } catch (error) {
      log('⚠️  Unit tests failed, but setup continues...', 'yellow');
    }

    log('\n📊 Test Coverage Report', 'bright');
    log('======================', 'bright');
    log('• Unit Tests: npm run test:coverage', 'cyan');
    log('• E2E Tests: npm run test:e2e', 'cyan');
    log('• E2E Tests (UI): npm run test:e2e:ui', 'cyan');
    log('• All Tests: npm run test:all', 'cyan');
    log('• Test Runner: node scripts/test-runner.js', 'cyan');

    log('\n📚 Documentation', 'bright');
    log('===============', 'bright');
    log('• Testing Guide: FRONTEND_TESTING.md', 'cyan');
    log('• Test Structure: src/__tests__/', 'cyan');
    log('• E2E Tests: e2e/', 'cyan');

    log('\n🎉 Testing environment setup complete!', 'green');
    log('\nNext steps:', 'bright');
    log('1. Start the backend server: cd ../backend && python -m uvicorn main:app --reload', 'cyan');
    log('2. Start the frontend: npm start', 'cyan');
    log('3. Run tests: npm run test:all', 'cyan');

  } catch (error) {
    log(`\n💥 Setup failed: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Handle process termination
process.on('SIGINT', () => {
  log('\n\n⏹️  Setup interrupted', 'yellow');
  process.exit(1);
});

process.on('SIGTERM', () => {
  log('\n\n⏹️  Setup terminated', 'yellow');
  process.exit(1);
});

setupTests(); 