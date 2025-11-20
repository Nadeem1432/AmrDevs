import os
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers import deserialize
from django.core.serializers.base import DeserializationError
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Load a JSON fixture and skip duplicates or missing related objects.'

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Path to the JSON fixture file')

    def handle(self, *args, **options):
        filepath = options['filepath']

        if not os.path.exists(filepath):
            raise CommandError(f"File '{filepath}' does not exist.")

        try:
            with open(filepath, 'r') as f:
                objects = list(deserialize('json', f))
        except DeserializationError as e:
            raise CommandError(
                f"Failed to deserialize JSON fixture '{filepath}'. "
                f"The file may be invalid JSON or not a proper Django fixture. "
                f"Original error: {e}"
            )
        except Exception as e:
            raise CommandError(
                f"Unexpected error while reading '{filepath}': {e}"
            )

        skipped_duplicates = 0
        skipped_missing_related = 0
        saved = 0

        for obj in objects:
            try:
                obj.save()
                saved += 1
            except IntegrityError:
                skipped_duplicates += 1
                self.stdout.write(self.style.WARNING(
                    f"Skipped duplicate: {obj.object.__class__.__name__} (pk={getattr(obj.object, 'pk', 'unknown')})"
                ))
            except (ContentType.DoesNotExist, ObjectDoesNotExist) as e:
                skipped_missing_related += 1
                self.stdout.write(self.style.WARNING(
                    f"Skipped due to missing related object: {obj.object.__class__.__name__} (pk={getattr(obj.object, 'pk', 'unknown')}) — {e}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Unexpected error for object {obj.object.__class__.__name__} (pk={getattr(obj.object, 'pk', 'unknown')}): {e}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"Finished loading data. Saved: {saved}, "
            f"Skipped duplicates: {skipped_duplicates}, "
            f"Skipped missing relations: {skipped_missing_related}."
        ))
