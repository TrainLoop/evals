#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const ROOT = path.join(__dirname, '..', '_bundle');
const PORT = process.env.PORT || '8888';

console.log(`🚀  TrainLoop Studio → http://localhost:${PORT}`);

// Set environment variables
process.env.PORT = PORT;
process.env.NODE_ENV = 'production';

// Ensure TRAINLOOP_DATA_FOLDER is set
if (!process.env.TRAINLOOP_DATA_FOLDER) {
    console.error('Error: TRAINLOOP_DATA_FOLDER environment variable is not set');
    console.error('Please set this variable to point to your TrainLoop data directory');
    process.exit(1);
}

// Verify that the data folder exists
const dataFolder = process.env.TRAINLOOP_DATA_FOLDER;
if (!fs.existsSync(dataFolder)) {
    console.error(`Error: Data folder does not exist: ${dataFolder}`);
    console.error('Please create this directory or specify a different TRAINLOOP_DATA_FOLDER');
    process.exit(1);
}

console.log(`Using data folder: ${dataFolder}`);

// Change working directory to the bundle directory
process.chdir(ROOT);

// Function to detect platform and architecture
function getPlatformPackage() {
    const platform = process.platform;
    const arch = process.arch;
    
    // Map Node.js platform/arch to DuckDB package names
    if (platform === 'darwin') {
        if (arch === 'arm64') return '@duckdb/node-bindings-darwin-arm64';
        if (arch === 'x64') return '@duckdb/node-bindings-darwin-x64';
    } else if (platform === 'linux') {
        if (arch === 'arm64') return '@duckdb/node-bindings-linux-arm64';
        if (arch === 'x64') return '@duckdb/node-bindings-linux-x64';
    } else if (platform === 'win32') {
        if (arch === 'x64') return '@duckdb/node-bindings-win32-x64';
    }
    
    return null;
}

// Check if DuckDB bindings are available
function checkDuckDBBindings() {
    try {
        // Try to require the DuckDB module to see if bindings are available
        require.resolve('@duckdb/node-api');
        // If successful, also check the specific bindings
        const bindingsPackage = getPlatformPackage();
        if (bindingsPackage) {
            try {
                const bindingsPath = require.resolve(path.join(bindingsPackage, 'duckdb.node'));
                return fs.existsSync(bindingsPath);
            } catch {
                return false;
            }
        }
        return true;
    } catch {
        return false;
    }
}

// Install DuckDB bindings if missing
function installDuckDBBindings() {
    const bindingsPackage = getPlatformPackage();
    
    if (!bindingsPackage) {
        console.error(`Error: Unsupported platform/architecture: ${process.platform}/${process.arch}`);
        console.error('DuckDB bindings are not available for this system.');
        process.exit(1);
    }
    
    // Check if npm is available
    try {
        execSync('npm --version', { stdio: 'ignore' });
    } catch {
        console.error('❌ npm is not available. Please ensure Node.js and npm are installed.');
        console.error('Visit https://nodejs.org/ for installation instructions.');
        process.exit(1);
    }
    
    console.log(`📦 Installing DuckDB bindings for ${process.platform}-${process.arch}...`);
    console.log(`   Package: ${bindingsPackage}`);
    
    try {
        // Install the platform-specific bindings package
        execSync(`npm install --no-save --no-audit --no-fund --loglevel=error ${bindingsPackage}`, {
            stdio: ['ignore', 'pipe', 'pipe'],
            cwd: ROOT
        });
        console.log('✅ DuckDB bindings installed successfully');
    } catch (error) {
        console.error('❌ Failed to install DuckDB bindings');
        console.error('Error:', error.message);
        console.error('\nYou can try installing manually:');
        console.error(`  cd ${ROOT}`);
        console.error(`  npm install ${bindingsPackage}`);
        process.exit(1);
    }
}

// Check and install DuckDB bindings if needed
if (!checkDuckDBBindings()) {
    installDuckDBBindings();
}

// Directly require the server file instead of spawning a process
try {
    require(path.join(ROOT, 'server.js'));
} catch (error) {
    console.error('Error starting TrainLoop Studio:', error);
    process.exit(1);
}

// Handle termination signals
['SIGINT', 'SIGTERM'].forEach(sig => {
    process.on(sig, () => process.exit(0));
});
