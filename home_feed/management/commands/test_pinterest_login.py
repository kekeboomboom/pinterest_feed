from django.core.management.base import BaseCommand
from home_feed.services import get_pinterest_cookies_python
import os
import json

class Command(BaseCommand):
    help = 'Test Pinterest login and cookie retrieval'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Testing Pinterest Login Method')
        self.stdout.write('=' * 60)
        
        # Check if .env file exists
        if not os.path.exists('.env'):
            self.stdout.write('❌ .env file not found!')
            self.stdout.write('Please create .env file with:')
            self.stdout.write('ACCOUNT=your_email@example.com')
            self.stdout.write('password=your_password')
            return
        
        # Check if cookies file already exists
        if os.path.exists('cookies.json'):
            self.stdout.write('⚠️  cookies.json already exists')
            response = input('Do you want to overwrite it? (y/n): ')
            if response.lower() != 'y':
                self.stdout.write('Cancelled.')
                return
        
        # Test the Pinterest login method
        success = get_pinterest_cookies_python()
        
        if success:
            self.stdout.write('✅ Pinterest login test completed successfully!')
            
            # Verify cookies file was created and contains data
            if os.path.exists('cookies.json'):
                try:
                    with open('cookies.json', 'r') as f:
                        cookies = json.load(f)
                    
                    self.stdout.write(f'📁 Cookie file size: {os.path.getsize("cookies.json")} bytes')
                    self.stdout.write(f'🍪 Number of cookies: {len(cookies)}')
                    self.stdout.write(f'📍 Cookie file location: {os.path.abspath("cookies.json")}')
                    
                    # Show first few cookie names (without values for security)
                    if cookies:
                        cookie_names = [cookie['name'] for cookie in cookies[:5]]
                        self.stdout.write(f'🔑 Sample cookie names: {", ".join(cookie_names)}')
                    
                except json.JSONDecodeError:
                    self.stdout.write('❌ Cookie file contains invalid JSON')
                except Exception as e:
                    self.stdout.write(f'❌ Error reading cookie file: {e}')
            else:
                self.stdout.write('❌ Cookie file was not created')
        else:
            self.stdout.write('❌ Pinterest login test failed')
            self.stdout.write('💡 Check your .env file credentials and try again') 
