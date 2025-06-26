from django.core.management.base import BaseCommand
from home_feed.models import APIKey


class Command(BaseCommand):
    help = 'Create a new API key for authentication'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            type=str,
            help='Descriptive name for the API key'
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Create the API key as inactive (default: active)'
        )

    def handle(self, *args, **options):
        name = options['name']
        is_active = not options['inactive']
        
        try:
            # Create the API key
            api_key = APIKey.objects.create(
                name=name,
                is_active=is_active
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ API Key created successfully!')
            )
            self.stdout.write(f'Name: {api_key.name}')
            self.stdout.write(f'Key: {api_key.key}')
            self.stdout.write(f'Active: {api_key.is_active}')
            self.stdout.write(f'Created: {api_key.created_at}')
            
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  Important: Save this API key securely!')
            )
            self.stdout.write('You won\'t be able to see the full key again in the admin interface.')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n🔑 Use this header for authentication:')
            )
            self.stdout.write(f'Authorization: Api-Key {api_key.key}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating API key: {str(e)}')
            )