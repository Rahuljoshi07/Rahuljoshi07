#!/usr/bin/env python3
"""
GitHub Profile Dashboard Updater
Automatically updates the contribution dashboard in your GitHub profile README
"""

import os
import requests
import json
from datetime import datetime
import re

class DashboardUpdater:
    def __init__(self, github_token, bot_repo_owner, bot_repo_name, profile_repo_owner, profile_repo_name):
        self.github_token = github_token
        self.bot_repo_owner = bot_repo_owner
        self.bot_repo_name = bot_repo_name
        self.profile_repo_owner = profile_repo_owner
        self.profile_repo_name = profile_repo_name
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_contribution_data(self):
        """Fetch contribution data from the bot repository"""
        try:
            # Try to get contributions.json from the bot repo
            url = f'https://api.github.com/repos/{self.bot_repo_owner}/{self.bot_repo_name}/contents/contributions.json'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                content = response.json()
                # Decode base64 content
                import base64
                decoded_content = base64.b64decode(content['content']).decode('utf-8')
                return json.loads(decoded_content)
            else:
                print(f"Could not fetch contributions.json: {response.status_code}")
                return self.get_default_data()
                
        except Exception as e:
            print(f"Error fetching contribution data: {e}")
            return self.get_default_data()
    
    def get_default_data(self):
        """Return default contribution data"""
        return {
            "stats": {
                "totalIssues": 0,
                "totalPRs": 0,
                "totalComments": 0,
                "successRate": 0
            },
            "issues": [],
            "pullRequests": [],
            "comments": []
        }
    
    def calculate_success_rate(self, data):
        """Calculate success rate percentage"""
        total_contributions = data['stats']['totalIssues'] + data['stats']['totalPRs'] + data['stats']['totalComments']
        if total_contributions == 0:
            return 0
        
        successful = data['stats'].get('acceptedPRs', 0) + data['stats'].get('closedIssues', 0)
        return round((successful / total_contributions) * 100, 1)
    
    def calculate_streak(self, data):
        """Calculate contribution streak"""
        # Simple streak calculation based on recent activity
        if data['stats']['totalIssues'] + data['stats']['totalPRs'] + data['stats']['totalComments'] > 0:
            return "1 Day"  # Simplified for now
        return "0 Days"
    
    def generate_dashboard_html(self, data):
        """Generate the HTML for the dashboard section"""
        total_contributions = data['stats']['totalIssues'] + data['stats']['totalPRs'] + data['stats']['totalComments']
        success_rate = self.calculate_success_rate(data)
        streak = self.calculate_streak(data)
        
        # Count active repositories
        active_repos = len(set([
            *[issue.get('repository', 'unknown') for issue in data.get('issues', [])],
            *[pr.get('repository', 'unknown') for pr in data.get('pullRequests', [])],
            *[comment.get('repository', 'unknown') for comment in data.get('comments', [])]
        ]))
        
        # Determine colors based on values
        success_color = "brightgreen" if success_rate >= 70 else "orange" if success_rate >= 50 else "red"
        status_color = "brightgreen" if total_contributions > 0 else "yellow"
        
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        dashboard_html = f"""<!-- START_BOT_DASHBOARD -->
<div align="center">
  <table>
    <tr>
      <td align="center">
        <h3>📈 Daily Contributions</h3>
        <img src="https://img.shields.io/badge/Issues-{data['stats']['totalIssues']}-brightgreen?style=for-the-badge&logo=github" alt="Issues Created"/>
        <img src="https://img.shields.io/badge/PRs-{data['stats']['totalPRs']}-blue?style=for-the-badge&logo=git" alt="Pull Requests"/>
        <img src="https://img.shields.io/badge/Comments-{data['stats']['totalComments']}-orange?style=for-the-badge&logo=comment" alt="Comments"/>
      </td>
      <td align="center">
        <h3>🎯 Success Rate</h3>
        <img src="https://img.shields.io/badge/Success_Rate-{success_rate}%25-{success_color}?style=for-the-badge" alt="Success Rate"/>
        <img src="https://img.shields.io/badge/Active_Repos-{active_repos}-purple?style=for-the-badge" alt="Active Repositories"/>
      </td>
    </tr>
    <tr>
      <td align="center">
        <h3>📊 Total Stats</h3>
        <img src="https://img.shields.io/badge/Total_Contributions-{total_contributions}-gold?style=for-the-badge" alt="Total Contributions"/>
        <img src="https://img.shields.io/badge/Last_Activity-Today-green?style=for-the-badge" alt="Last Activity"/>
      </td>
      <td align="center">
        <h3>🔥 Current Streak</h3>
        <img src="https://img.shields.io/badge/Contribution_Streak-{streak}-fire?style=for-the-badge" alt="Contribution Streak"/>
        <img src="https://img.shields.io/badge/Status-Active-{status_color}?style=for-the-badge" alt="Bot Status"/>
      </td>
    </tr>
  </table>
</div>

<div align="center">
  <h4>🕐 Last Updated: {current_time}</h4>
  <a href="https://github.com/{self.bot_repo_owner}/{self.bot_repo_name}" target="_blank">
    <img src="https://img.shields.io/badge/View_Bot_Repository-181717?style=for-the-badge&logo=github" alt="Bot Repository"/>
  </a>
</div>
<!-- END_BOT_DASHBOARD -->"""
        
        return dashboard_html
    
    def update_profile_readme(self, dashboard_html):
        """Update the profile README with new dashboard data"""
        try:
            # Get current README content
            url = f'https://api.github.com/repos/{self.profile_repo_owner}/{self.profile_repo_name}/contents/README.md'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"Could not fetch README.md: {response.status_code}")
                return False
            
            content = response.json()
            import base64
            current_content = base64.b64decode(content['content']).decode('utf-8')
            
            # Replace the dashboard section
            pattern = r'<!-- START_BOT_DASHBOARD -->.*?<!-- END_BOT_DASHBOARD -->'
            new_content = re.sub(pattern, dashboard_html, current_content, flags=re.DOTALL)
            
            # Encode the new content
            encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
            
            # Update the file
            update_data = {
                'message': '🤖 Auto-update contribution dashboard',
                'content': encoded_content,
                'sha': content['sha']
            }
            
            response = requests.put(url, headers=self.headers, json=update_data)
            
            if response.status_code == 200:
                print("✅ Profile README updated successfully!")
                return True
            else:
                print(f"❌ Failed to update README: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"Error updating profile README: {e}")
            return False
    
    def run(self):
        """Main execution method"""
        print("🚀 Starting dashboard update...")
        
        # Get contribution data
        print("📊 Fetching contribution data...")
        data = self.get_contribution_data()
        
        # Generate dashboard HTML
        print("🎨 Generating dashboard HTML...")
        dashboard_html = self.generate_dashboard_html(data)
        
        # Update profile README
        print("📝 Updating profile README...")
        success = self.update_profile_readme(dashboard_html)
        
        if success:
            print("🎉 Dashboard update completed successfully!")
        else:
            print("❌ Dashboard update failed!")
        
        return success

def main():
    """Main function"""
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('BOT_GITHUB_TOKEN')
    
    if not github_token:
        print("❌ GitHub token not found! Please set GITHUB_TOKEN or BOT_GITHUB_TOKEN environment variable.")
        return
    
    updater = DashboardUpdater(
        github_token=github_token,
        bot_repo_owner='Rahuljoshi07',
        bot_repo_name='github-contribution-bot',
        profile_repo_owner='Rahuljoshi07',
        profile_repo_name='Rahuljoshi07'
    )
    
    updater.run()

if __name__ == "__main__":
    main()
