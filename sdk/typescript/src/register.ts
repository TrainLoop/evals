/**
 * Entry point for NODE_OPTIONS="--require=trainloop-llm-logging/register"
 * This file automatically initializes the TrainLoop SDK with flush_immediately=true
 * without requiring any code changes.
 */

import { collect } from './index';

// Auto-initialize with flush_immediately=true when using --require flag
collect(true);