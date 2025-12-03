"""
Management command to test SMS functionality
Usage: python manage.py test_sms <phone_number>
"""
from django.core.management.base import BaseCommand
from etailoring.sms_service import SemaphoreSMS


class Command(BaseCommand):
    help = 'Test SMS functionality by sending a test message'

    def add_arguments(self, parser):
        parser.add_argument(
            'phone_number',
            type=str,
            help='Phone number to send test SMS to (e.g., 09998887777)'
        )
        parser.add_argument(
            '--customer-name',
            type=str,
            default='Test Customer',
            help='Customer name for the message'
        )
        parser.add_argument(
            '--order-id',
            type=int,
            default=1,
            help='Order ID for the message'
        )

    def handle(self, *args, **options):
        phone_number = options['phone_number']
        customer_name = options['customer_name']
        order_id = options['order_id']

        self.stdout.write(
            self.style.SUCCESS(f'Sending test SMS to {phone_number}...')
        )

        success, message = SemaphoreSMS.notify_customer_ready_for_pickup(
            customer_name=customer_name,
            customer_phone=phone_number,
            order_id=order_id
        )

        if success:
            self.stdout.write(
                self.style.SUCCESS(f'✓ SMS sent successfully!')
            )
            self.stdout.write(f'Response: {message}')
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send SMS')
            )
            self.stdout.write(f'Error: {message}')
