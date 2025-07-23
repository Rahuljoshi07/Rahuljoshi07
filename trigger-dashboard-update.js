#!/usr/bin/env node

/**
 * GitHub Repository Dispatch Trigger
 * 
 * This script triggers the dashboard update workflow in the profile repository
 * after the contribution bot completes its run.
 */

const https = require('https');

async function triggerDashboardUpdate() {
  const token = process.env.GITHUB_TOKEN;
  
  if (!token) {
    console.log('⚠️ No GitHub token found, skipping dashboard update trigger');
    return;
  }

  console.log('🚀 Triggering dashboard update workflow...');

  const data = JSON.stringify({
    event_type: 'update-dashboard',
    client_payload: {
      timestamp: new Date().toISOString(),
      trigger: 'bot-completed',
      source: 'contribution-bot'
    }
  });

  const options = {
    hostname: 'api.github.com',
    port: 443,
    path: '/repos/Rahuljoshi07/Rahuljoshi07/dispatches',
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'contribution-bot-trigger',
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 204) {
          console.log('✅ Dashboard update workflow triggered successfully!');
          console.log('🔗 Check your profile repository Actions tab for progress');
          resolve();
        } else {
          console.log(`⚠️ Unexpected response status: ${res.statusCode}`);
          console.log(`Response: ${responseData}`);
          resolve(); // Don't fail the bot run for this
        }
      });
    });

    req.on('error', (error) => {
      console.error('❌ Failed to trigger dashboard update:', error.message);
      resolve(); // Don't fail the bot run for this
    });

    req.write(data);
    req.end();
  });
}

// Export for use in other scripts
module.exports = { triggerDashboardUpdate };

// Run if called directly
if (require.main === module) {
  triggerDashboardUpdate().catch(console.error);
}
