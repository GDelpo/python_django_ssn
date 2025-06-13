import logging
import os
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger("operaciones")


class Command(BaseCommand):
    help = "Remove preview files older than the specified age."

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-age-minutes",
            type=int,
            default=settings.PREVIEW_MAX_AGE_MINUTES,
            help="Maximum age in minutes for preview files to keep",
        )

    def handle(self, *args, **options):
        max_age = options["max_age_minutes"]
        cutoff = time.time() - max_age * 60

        logger.info("Cleaning preview files older than %s minute(s)", max_age)

        preview_dir = Path(settings.MEDIA_ROOT) / "previews"
        if not preview_dir.exists():
            msg = f"Directory {preview_dir} does not exist."
            logger.warning(msg)
            self.stdout.write(self.style.NOTICE(msg))
            return

        removed = 0
        for path in preview_dir.iterdir():
            if path.is_file():
                try:
                    mtime = os.path.getmtime(path)
                    if mtime < cutoff:
                        path.unlink()
                        removed += 1
                        logger.debug("Deleted preview %s", path)
                except FileNotFoundError:
                    continue
                except Exception as exc:
                    logger.error("Failed to remove %s: %s", path, exc)
                    self.stderr.write(f"Failed to remove {path}: {exc}")

        logger.info("Removed %s preview file(s)", removed)
        self.stdout.write(self.style.SUCCESS(f"Removed {removed} file(s)."))
