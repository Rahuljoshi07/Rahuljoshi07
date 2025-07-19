#!/usr/bin/env python3
"""
Real-Time Dashboard Monitor
Monitors the bot repository for changes and triggers immediate dashboard updates
"""

import os
import time
import requests
import json
from datetime import datetime, timedelta
import threading
import hashlib

class RealTimeDashboardMonitor:
    def __init__(self, github_token, check_interval=300):  # 5 minutes
        self.github_token = github_token
        self.check_interval = check_interval
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.last_update_hash = None
        self.monitoring = False
        
    def get_bot_repo_latest_commit(self):
        """Get the latest commit hash from the bot repository"""
        try:
            url = 'https://api.github.com/repos/Rahuljoshi07/github-contribution-bot/commits/main'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                commit_data = response.json()
                return commit_data['sha']
            else:
                print(f"❌ Failed to fetch latest commit: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching latest commit: {e}")
            return None
    
    def get_contributions_file_hash(self):
        """Get the hash of the contributions.json file"""
        try:
            url = 'https://api.github.com/repos/Rahuljoshi07/github-contribution-bot/contents/contributions.json'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                content_data = response.json()
                return content_data['sha']
            else:
                print(f"❌ Failed to fetch contributions file: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching contributions file: {e}")
            return None
    
    def trigger_dashboard_update(self):
        """Trigger the dashboard update workflow"""
        try:
            url = 'https://api.github.com/repos/Rahuljoshi07/Rahuljoshi07/dispatches'
            data = {
                'event_type': 'update-dashboard',
                'client_payload': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'trigger': 'real-time-monitor'
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 204:
                print("✅ Dashboard update triggered successfully!")
                return True
            else:
                print(f"❌ Failed to trigger dashboard update: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error triggering dashboard update: {e}")
            return False
    
    def run_dashboard_update_directly(self):
        """Run the dashboard update script directly"""
        try:
            from update_dashboard import DashboardUpdater
            
            updater = DashboardUpdater(
                github_token=self.github_token,
                bot_repo_owner='Rahuljoshi07',
                bot_repo_name='github-contribution-bot',
                profile_repo_owner='Rahuljoshi07',
                profile_repo_name='Rahuljoshi07'
            )
            
            return updater.run()
            
        except Exception as e:
            print(f"❌ Error running dashboard update directly: {e}")
            return False
    
    def check_for_updates(self):
        """Check if the bot repository has been updated"""
        current_hash = self.get_contributions_file_hash()
        
        if current_hash is None:
            return False
            
        if self.last_update_hash is None:
            self.last_update_hash = current_hash
            print(f"🔍 Initial hash set: {current_hash[:8]}...")
            return False
            
        if current_hash != self.last_update_hash:
            print(f"🔥 Update detected! Hash changed from {self.last_update_hash[:8]}... to {current_hash[:8]}...")
            self.last_update_hash = current_hash
            return True
            
        return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("🚀 Starting real-time dashboard monitor...")
        print(f"📊 Checking for updates every {self.check_interval} seconds")
        
        while self.monitoring:
            try:
                if self.check_for_updates():
                    print("🔄 Bot repository updated, triggering dashboard update...")
                    
                    # Try to trigger via GitHub Actions first
                    if not self.trigger_dashboard_update():
                        print("⚠️ GitHub Actions trigger failed, running update directly...")
                        self.run_dashboard_update_directly()
                
                # Wait for the next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitor stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
    
    def start_monitoring(self):
        """Start monitoring in a separate thread"""
        if self.monitoring:
            print("⚠️ Monitor is already running!")
            return
            
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        print("🛑 Stopping monitor...")

def main():
    """Main function"""
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('BOT_GITHUB_TOKEN')
    
    if not github_token:
        print("❌ GitHub token not found! Please set GITHUB_TOKEN or BOT_GITHUB_TOKEN environment variable.")
        return
    
    # Create monitor with 5-minute intervals (300 seconds)
    monitor = RealTimeDashboardMonitor(github_token, check_interval=300)
    
    try:
        # Start monitoring
        monitor_thread = monitor.start_monitoring()
        
        # Keep the main thread alive
        while monitor.monitoring:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down monitor...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
