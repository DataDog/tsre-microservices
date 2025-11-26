#!/usr/bin/env node
// Main orchestrator for Playwright-based load generator
const { runUserSession } = require('./user-journeys');
const logger = require('./logger');

const NUM_USERS = parseInt(process.env.USERS || '10', 10);
const FRONTEND_URL = process.env.FRONTEND_ADDR 
  ? `http://${process.env.FRONTEND_ADDR}` 
  : 'http://frontend:8088';

logger.info('Playwright Load Generator Starting', {
  frontend_url: FRONTEND_URL,
  num_users: NUM_USERS,
  environment: process.env.DD_ENV || 'unknown'
});

// Wait for frontend to be ready
async function waitForFrontend() {
  const http = require('http');
  const url = new URL(FRONTEND_URL);
  
  return new Promise((resolve) => {
    const checkInterval = setInterval(() => {
      const options = {
        hostname: url.hostname,
        port: url.port || 80,
        path: '/',
        method: 'GET',
        timeout: 2000
      };
      
      const req = http.request(options, (res) => {
        if (res.statusCode === 200) {
          logger.info('Frontend is ready');
          clearInterval(checkInterval);
          resolve();
        }
      });
      
      req.on('error', (err) => {
        logger.debug('Waiting for frontend to be ready');
      });
      
      req.end();
    }, 2000);
  });
}

// Main function
async function main() {
  // Wait for frontend
  await waitForFrontend();
  
  logger.info('Spawning user sessions', { num_users: NUM_USERS });
  
  // Spawn concurrent user sessions
  const userPromises = [];
  for (let i = 1; i <= NUM_USERS; i++) {
    logger.info('Starting user session', { user_id: i });
    userPromises.push(runUserSession(i));
    
    // Stagger user startup slightly
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  logger.info('All users spawned and running', { num_users: NUM_USERS });
  
  // Handle graceful shutdown
  process.on('SIGTERM', () => {
    logger.info('Received SIGTERM, shutting down gracefully');
    process.exit(0);
  });
  
  process.on('SIGINT', () => {
    logger.info('Received SIGINT, shutting down gracefully');
    process.exit(0);
  });
  
  // Wait for all users (runs forever)
  await Promise.all(userPromises);
}

main().catch((error) => {
  logger.error('Fatal error', { error: error.message, stack: error.stack });
  process.exit(1);
});

