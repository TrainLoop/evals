#!/usr/bin/env node
const path = require('path');
const fs = require('fs');

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
