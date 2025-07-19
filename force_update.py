#!/usr/bin/env python3
"""
Force Dashboard Update Script
Manually updates the dashboard with current timestamp to verify it's working
"""

import os
import re
from datetime import datetime

def force_update_dashboard():
    """Force update the dashboard with current timestamp"""
    
    # Get current timestamp
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Read current README
    try:
        with open('README.md', 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"❌ Error reading README: {e}")
        return False
    
    # Create updated dashboard with current timestamp
    updated_dashboard = f"""<!-- START_BOT_DASHBOARD -->
<div align="center">
  <table>
    <tr>
      <td align="center">
        <h3>📈 Daily Contributions</h3>
        <img src="https://img.shields.io/badge/Issues-1-brightgreen?style=for-the-badge&logo=github" alt="Issues Created"/>
        <img src="https://img.shields.io/badge/PRs-1-blue?style=for-the-badge&logo=git" alt="Pull Requests"/>
        <img src="https://img.shields.io/badge/Comments-1-orange?style=for-the-badge&logo=comment" alt="Comments"/>
      </td>
      <td align="center">
        <h3>🎯 Success Rate</h3>
        <img src="https://img.shields.io/badge/Success_Rate-0%25-red?style=for-the-badge" alt="Success Rate"/>
        <img src="https://img.shields.io/badge/Active_Repos-3-purple?style=for-the-badge" alt="Active Repositories"/>
      </td>
    </tr>
    <tr>
      <td align="center">
        <h3>📊 Total Stats</h3>
        <img src="https://img.shields.io/badge/Total_Contributions-3-gold?style=for-the-badge" alt="Total Contributions"/>
        <img src="https://img.shields.io/badge/Last_Activity-Today-green?style=for-the-badge" alt="Last Activity"/>
      </td>
      <td align="center">
        <h3>🔥 Current Streak</h3>
        <img src="https://img.shields.io/badge/Contribution_Streak-1_Day-fire?style=for-the-badge" alt="Contribution Streak"/>
        <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Bot Status"/>
      </td>
    </tr>
  </table>
</div>

<div align="center">
  <h4>🕐 Last Updated: {current_time}</h4>
  <a href="https://github.com/Rahuljoshi07/github-contribution-bot" target="_blank">
    <img src="https://img.shields.io/badge/View_Bot_Repository-181717?style=for-the-badge&logo=github" alt="Bot Repository"/>
  </a>
</div>
<!-- END_BOT_DASHBOARD -->"""
    
    # Replace the dashboard section
    pattern = r'<!-- START_BOT_DASHBOARD -->.*?<!-- END_BOT_DASHBOARD -->'
    new_content = re.sub(pattern, updated_dashboard, content, flags=re.DOTALL)
    
    # Write updated content
    try:
        with open('README.md', 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"✅ Dashboard updated with timestamp: {current_time}")
        return True
    except Exception as e:
        print(f"❌ Error writing README: {e}")
        return False

if __name__ == "__main__":
    if force_update_dashboard():
        print("🎉 Dashboard update completed!")
    else:
        print("❌ Dashboard update failed!")
