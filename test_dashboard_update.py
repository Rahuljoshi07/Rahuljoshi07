#!/usr/bin/env python3
"""
Dashboard Update Test Script
Tests the dashboard update functionality
"""

import os
import sys
from update_dashboard import DashboardUpdater

def test_dashboard_update():
    """Test the dashboard update functionality"""
    print("🧪 Testing Dashboard Update Functionality")
    print("=" * 50)
    
    # Check for GitHub token
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('BOT_GITHUB_TOKEN')
    
    if not github_token:
        print("❌ No GitHub token found!")
        print("Please set GITHUB_TOKEN environment variable")
        return False
    
    print("✅ GitHub token found")
    
    # Create updater instance
    updater = DashboardUpdater(
        github_token=github_token,
        bot_repo_owner='Rahuljoshi07',
        bot_repo_name='github-contribution-bot',
        profile_repo_owner='Rahuljoshi07',
        profile_repo_name='Rahuljoshi07'
    )
    
    # Test fetching contribution data
    print("\n📊 Testing contribution data fetch...")
    data = updater.get_contribution_data()
    
    if data:
        print("✅ Successfully fetched contribution data")
        print(f"   - Issues: {data.get('stats', {}).get('totalIssues', 0)}")
        print(f"   - Pull Requests: {data.get('stats', {}).get('totalPRs', 0)}")
        print(f"   - Comments: {data.get('stats', {}).get('totalComments', 0)}")
    else:
        print("❌ Failed to fetch contribution data")
        return False
    
    # Test HTML generation
    print("\n🎨 Testing dashboard HTML generation...")
    dashboard_html = updater.generate_dashboard_html(data)
    
    if dashboard_html and "START_BOT_DASHBOARD" in dashboard_html:
        print("✅ Successfully generated dashboard HTML")
        print(f"   - HTML length: {len(dashboard_html)} characters")
    else:
        print("❌ Failed to generate dashboard HTML")
        return False
    
    # Test README update (dry run first)
    print("\n📝 Testing README update...")
    
    # Ask user if they want to actually update
    response = input("Do you want to actually update the README? (y/n): ").lower().strip()
    
    if response == 'y':
        success = updater.update_profile_readme(dashboard_html)
        if success:
            print("✅ Successfully updated README!")
        else:
            print("❌ Failed to update README")
            return False
    else:
        print("ℹ️ Skipping actual README update (dry run)")
    
    print("\n🎉 All tests completed successfully!")
    return True

if __name__ == "__main__":
    if test_dashboard_update():
        print("\n✅ Dashboard update system is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Dashboard update system has issues!")
        sys.exit(1)
