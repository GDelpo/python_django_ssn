import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from ...models import BaseRequestModel

logger = logging.getLogger("operaciones")

class Command(BaseCommand):
    help = "Deletes unsent and empty requests older than X days"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Age in days to consider for deletion (default: 7)'
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff = timezone.now() - timedelta(days=days)

        # Select requests not sent and created before the cutoff
        qs = BaseRequestModel.objects.filter(
            send_at__isnull=True,
            created_at__lt=cutoff
        )

        # Filter requests with no associated operations (adjust related_name as needed)
        empty = [req for req in qs if not req.operations.exists()]

        count = len(empty)
        deleted_ids = [req.id for req in empty]
        for req in empty:
            req.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {count} unsent and empty requests older than {days} days."
            )
        )
        logger.info(
            f"[clean_requests] Deleted {count} requests (IDs: {deleted_ids}) older than {days} days."
        )
