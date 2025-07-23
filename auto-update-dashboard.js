#!/usr/bin/env node

/**
 * Automated GitHub Contribution Dashboard Updater
 * 
 * This script automatically:
 * 1. Runs your contribution bot to generate new contributions
 * 2. Copies the updated contributions.json to your profile repo
 * 3. Updates the dashboard with new stats
 * 4. Commits and pushes the changes to GitHub
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const execAsync = util.promisify(exec);

// Configuration
const CONFIG = {
  botProjectPath: 'C:\\Users\\Lenovo\\github-contribution-bot',
  profileRepoPath: 'C:\\Users\\Lenovo\\Rahuljoshi07',
  botScript: 'run-production.js', // or 'index.js' depending on which you want to run
  maxRetries: 3,
  delayBetweenSteps: 2000 // 2 seconds
};

console.log('🚀 Starting Automated GitHub Contribution Dashboard Update...\n');
console.log('=' * 70);
console.log('🤖 AUTOMATED DASHBOARD UPDATER');
console.log('=' * 70);

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function logStep(step, message) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`📍 STEP ${step}: ${message}`);
  console.log(`${'='.repeat(60)}`);
}

async function runWithRetry(fn, retries = CONFIG.maxRetries) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      console.log(`⚠️ Attempt ${i + 1} failed: ${error.message}`);
      if (i === retries - 1) throw error;
      await sleep(CONFIG.delayBetweenSteps);
    }
  }
}

// Step 1: Run the contribution bot
async function runContributionBot() {
  await logStep(1, 'Running Contribution Bot');
  
  return new Promise((resolve, reject) => {
    console.log(`📂 Changing to bot directory: ${CONFIG.botProjectPath}`);
    console.log(`🤖 Running: node ${CONFIG.botScript}`);
    
    const botProcess = spawn('node', [CONFIG.botScript], {
      cwd: CONFIG.botProjectPath,
      stdio: 'pipe',
      shell: true
    });

    let output = '';
    let errorOutput = '';

    botProcess.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      process.stdout.write(text); // Show real-time output
    });

    botProcess.stderr.on('data', (data) => {
      const text = data.toString();
      errorOutput += text;
      process.stderr.write(text);
    });

    botProcess.on('close', (code) => {
      if (code === 0) {
        console.log('\n✅ Contribution bot completed successfully!');
        resolve(output);
      } else {
        reject(new Error(`Bot exited with code ${code}. Error: ${errorOutput}`));
      }
    });

    botProcess.on('error', (error) => {
      reject(new Error(`Failed to start bot: ${error.message}`));
    });

    // Set a timeout to prevent hanging
    setTimeout(() => {
      botProcess.kill();
      reject(new Error('Bot execution timed out after 5 minutes'));
    }, 300000); // 5 minutes timeout
  });
}

// Step 2: Copy contributions.json to profile repo
async function copyContributionsData() {
  await logStep(2, 'Copying Contributions Data');
  
  const sourceFile = path.join(CONFIG.botProjectPath, 'contributions.json');
  const destFile = path.join(CONFIG.profileRepoPath, 'contributions.json');

  console.log(`📁 Source: ${sourceFile}`);
  console.log(`📁 Destination: ${destFile}`);

  if (!fs.existsSync(sourceFile)) {
    throw new Error('contributions.json not found in bot project. Bot may not have run successfully.');
  }

  // Copy the file
  fs.copyFileSync(sourceFile, destFile);
  
  // Verify the copy
  if (!fs.existsSync(destFile)) {
    throw new Error('Failed to copy contributions.json to profile repo');
  }

  // Read and display the data
  const contributionsData = JSON.parse(fs.readFileSync(destFile, 'utf8'));
  const totalContributions = contributionsData.stats.totalIssues + 
                             contributionsData.stats.totalPRs + 
                             contributionsData.stats.totalComments;

  console.log(`✅ Successfully copied contributions data`);
  console.log(`📊 Total contributions: ${totalContributions}`);
  console.log(`   Issues: ${contributionsData.stats.totalIssues}`);
  console.log(`   PRs: ${contributionsData.stats.totalPRs}`);
  console.log(`   Comments: ${contributionsData.stats.totalComments}`);
}

// Step 3: Update the dashboard
async function updateDashboard() {
  await logStep(3, 'Updating Dashboard');
  
  console.log(`📂 Running dashboard update in: ${CONFIG.profileRepoPath}`);
  
  try {
    const { stdout, stderr } = await execAsync('node update-profile-dashboard.js', {
      cwd: CONFIG.profileRepoPath
    });
    
    console.log(stdout);
    if (stderr) console.warn('Warnings:', stderr);
    
    console.log('✅ Dashboard updated successfully!');
  } catch (error) {
    throw new Error(`Dashboard update failed: ${error.message}`);
  }
}

// Step 4: Commit and push changes
async function commitAndPush() {
  await logStep(4, 'Committing and Pushing Changes');
  
  try {
    // Check if there are any changes
    console.log('🔍 Checking for changes...');
    const { stdout: statusOutput } = await execAsync('git status --porcelain', {
      cwd: CONFIG.profileRepoPath
    });

    if (!statusOutput.trim()) {
      console.log('ℹ️ No changes detected. Dashboard may already be up to date.');
      return;
    }

    console.log('📝 Changes detected:');
    console.log(statusOutput);

    // Add files
    console.log('➕ Adding files...');
    await execAsync('git add README.md contributions.json', {
      cwd: CONFIG.profileRepoPath
    });

    // Create commit message with timestamp and stats
    const contributionsData = JSON.parse(fs.readFileSync(
      path.join(CONFIG.profileRepoPath, 'contributions.json'), 'utf8'
    ));
    const totalContributions = contributionsData.stats.totalIssues + 
                               contributionsData.stats.totalPRs + 
                               contributionsData.stats.totalComments;
    
    const timestamp = new Date().toISOString().slice(0, 19).replace('T', ' ');
    const commitMessage = `🤖 Auto-update dashboard: ${totalContributions} contributions (${timestamp})`;

    // Commit changes
    console.log('💾 Committing changes...');
    console.log(`📝 Commit message: ${commitMessage}`);
    await execAsync(`git commit -m "${commitMessage}"`, {
      cwd: CONFIG.profileRepoPath
    });

    // Push to GitHub
    console.log('🚀 Pushing to GitHub...');
    await execAsync('git push origin main', {
      cwd: CONFIG.profileRepoPath
    });

    console.log('✅ Successfully committed and pushed changes!');
    console.log('🌐 Your GitHub profile dashboard is now updated!');
    
  } catch (error) {
    throw new Error(`Git operations failed: ${error.message}`);
  }
}

// Main automation function
async function runAutomation() {
  const startTime = Date.now();
  
  try {
    console.log('🎯 Starting full automation sequence...\n');

    // Step 1: Run contribution bot
    await runWithRetry(runContributionBot);
    await sleep(CONFIG.delayBetweenSteps);

    // Step 2: Copy contributions data
    await runWithRetry(copyContributionsData);
    await sleep(CONFIG.delayBetweenSteps);

    // Step 3: Update dashboard
    await runWithRetry(updateDashboard);
    await sleep(CONFIG.delayBetweenSteps);

    // Step 4: Commit and push
    await runWithRetry(commitAndPush);

    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(1);

    console.log('\n' + '='.repeat(70));
    console.log('🎉 AUTOMATION COMPLETED SUCCESSFULLY!');
    console.log('='.repeat(70));
    console.log(`⏱️ Total time: ${duration} seconds`);
    console.log('🌐 Your GitHub profile dashboard is now live with the latest data!');
    console.log('🔗 View your profile: https://github.com/Rahuljoshi07');
    console.log('\n💡 To run this automation again, simply execute:');
    console.log('   node auto-update-dashboard.js');

  } catch (error) {
    console.error('\n' + '='.repeat(70));
    console.error('❌ AUTOMATION FAILED');
    console.error('='.repeat(70));
    console.error(`💥 Error: ${error.message}`);
    console.error('\n🔧 Troubleshooting tips:');
    console.error('   1. Check your GitHub token in .env file');
    console.error('   2. Ensure both repositories exist and are accessible');
    console.error('   3. Verify git is configured with your credentials');
    console.error('   4. Check network connectivity');
    
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  runAutomation().catch(console.error);
}

module.exports = { runAutomation };
