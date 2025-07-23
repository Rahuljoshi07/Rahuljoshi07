#!/usr/bin/env node

/**
 * GitHub Contribution Dashboard Data to Markdown
 * 
 * This script updates your GitHub profile README dashboard
 * with dynamic badge styling using contribution data.
 */

const fs = require('fs');
const path = require('path');

console.log('🚀 Starting GitHub Contribution Dashboard Data Formatter...\n');

const contributionsFile = path.join(__dirname, 'contributions.json');
const readmeFile = path.join(__dirname, 'README.md');

try {
  // Load contributions data
  const contributionsData = JSON.parse(fs.readFileSync(contributionsFile, 'utf8'));
  const { issues, pullRequests, comments, stats } = contributionsData;

  // Format badges using contributions summary
  const badges = `![Total Contributions](https://img.shields.io/badge/Total_Contributions-${stats.totalIssues + stats.totalPRs + stats.totalComments}-gold?style=for-the-badge)\n` +
    `![Issues Created](https://img.shields.io/badge/Issues-${stats.totalIssues}-brightgreen?style=for-the-badge&logo=github)\n` +
    `![Pull Requests](https://img.shields.io/badge/PRs-${stats.totalPRs}-blue?style=for-the-badge&logo=git)\n` +
    `![Comments](https://img.shields.io/badge/Comments-${stats.totalComments}-orange?style=for-the-badge&logo=comment)\n` +
    `![Success Rate](https://img.shields.io/badge/Success_Rate-${stats.successRate}%25${stats.successRate > 0 ? '-red' : '-green'}?style=for-the-badge)\n`;

  // Load and update README content
  let readmeContent = fs.readFileSync(readmeFile, 'utf8');
  const dashboardStart = readmeContent.indexOf('<!-- START_BOT_DASHBOARD -->');
  const dashboardEnd = readmeContent.indexOf('<!-- END_BOT_DASHBOARD -->', dashboardStart);

  if(dashboardStart === -1 || dashboardEnd === -1) {
    console.error('Dashboard markers not found in README.md');
    process.exit(1);
  }

  const updatedContent = readmeContent.slice(0, dashboardStart) + `<!-- START_BOT_DASHBOARD -->\n${badges}\n<!-- END_BOT_DASHBOARD -->` + readmeContent.slice(dashboardEnd + '<!-- END_BOT_DASHBOARD -->'.length);

  // Save updated README
  fs.writeFileSync(readmeFile, updatedContent);

  console.log('✅ Dashboard data updated in README.md\n');
  console.log('🎯 Finalize dashboard by committing the changes to your profile repository.');

} catch (error) {
  console.error('❌ Failed to update dashboard:', error.message);
  console.error('Stack trace:', error.stack);
}
