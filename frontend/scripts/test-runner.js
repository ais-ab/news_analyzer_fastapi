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
  magenta: '\x1b[35m',
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

async function runUnitTests() {
  log('\n🧪 Running Unit Tests...', 'cyan');
  try {
    await runCommand('npm', ['run', 'test:coverage']);
    log('✅ Unit tests completed successfully!', 'green');
    return true;
  } catch (error) {
    log('❌ Unit tests failed!', 'red');
    return false;
  }
}

async function runE2ETests() {
  log('\n🌐 Running E2E Tests...', 'cyan');
  try {
    // Check if Playwright is installed
    if (!fs.existsSync(path.join(__dirname, '../node_modules/@playwright/test'))) {
      log('📦 Installing Playwright...', 'yellow');
      await runCommand('npx', ['playwright', 'install']);
    }
    
    await runCommand('npm', ['run', 'test:e2e']);
    log('✅ E2E tests completed successfully!', 'green');
    return true;
  } catch (error) {
    log('❌ E2E tests failed!', 'red');
    return false;
  }
}

async function runLinting() {
  log('\n🔍 Running Linting...', 'cyan');
  try {
    await runCommand('npm', ['run', 'lint']);
    log('✅ Linting passed!', 'green');
    return true;
  } catch (error) {
    log('❌ Linting failed!', 'red');
    return false;
  }
}

async function runTypeChecking() {
  log('\n📝 Running Type Checking...', 'cyan');
  try {
    await runCommand('npx', ['tsc', '--noEmit']);
    log('✅ Type checking passed!', 'green');
    return true;
  } catch (error) {
    log('❌ Type checking failed!', 'red');
    return false;
  }
}

async function main() {
  const args = process.argv.slice(2);
  const testType = args[0] || 'all';

  log('🚀 Frontend Test Runner', 'bright');
  log('=====================\n', 'bright');

  let results = {};

  try {
    switch (testType) {
      case 'unit':
        results.unit = await runUnitTests();
        break;
      
      case 'e2e':
        results.e2e = await runE2ETests();
        break;
      
      case 'lint':
        results.lint = await runLinting();
        break;
      
      case 'types':
        results.types = await runTypeChecking();
        break;
      
      case 'all':
      default:
        results.lint = await runLinting();
        results.types = await runTypeChecking();
        results.unit = await runUnitTests();
        results.e2e = await runE2ETests();
        break;
    }

    // Summary
    log('\n📊 Test Summary', 'bright');
    log('==============', 'bright');
    
    Object.entries(results).forEach(([test, passed]) => {
      const status = passed ? '✅ PASSED' : '❌ FAILED';
      const color = passed ? 'green' : 'red';
      log(`${test.toUpperCase()}: ${status}`, color);
    });

    const allPassed = Object.values(results).every(Boolean);
    if (allPassed) {
      log('\n🎉 All tests passed!', 'green');
      process.exit(0);
    } else {
      log('\n💥 Some tests failed!', 'red');
      process.exit(1);
    }

  } catch (error) {
    log(`\n💥 Test runner error: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Handle process termination
process.on('SIGINT', () => {
  log('\n\n⏹️  Test runner interrupted', 'yellow');
  process.exit(1);
});

process.on('SIGTERM', () => {
  log('\n\n⏹️  Test runner terminated', 'yellow');
  process.exit(1);
});

main(); 