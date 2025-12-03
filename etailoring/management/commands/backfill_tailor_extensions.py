from django.core.management.base import BaseCommand

from etailoring.models import Tailor, UserExtension


class Command(BaseCommand):
    help = 'Backfill missing UserExtension rows for existing Tailor objects (role=TAILOR)'

    def handle(self, *args, **options):
        created = 0
        missing_users = []
        for t in Tailor.objects.select_related('user').all():
            user = t.user
            if not hasattr(user, 'userextension'):
                try:
                    UserExtension.objects.create(user=user, role='TAILOR', phone_number=t.phone_number or '')
                    created += 1
                except Exception as e:
                    self.stderr.write(f"Failed to create extension for {user.username}: {e}")
                    missing_users.append(user.username)

        self.stdout.write(self.style.SUCCESS(f'Created {created} UserExtension(s) for Tailor users.'))
        if missing_users:
            self.stdout.write(self.style.WARNING('Failed or skipped for users: ' + ', '.join(missing_users)))
