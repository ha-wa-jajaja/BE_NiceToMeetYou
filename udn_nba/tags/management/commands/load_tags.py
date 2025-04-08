# tags/management/commands/load_tags.py
import json
import os

from django.core.management.base import BaseCommand
from tags.models import Tag


class Command(BaseCommand):
    help = "Load tags from fixture without creating duplicates"

    def handle(self, *args, **options):
        fixture_path = "tags/fixtures/default_data.json"
        with open(fixture_path, "r") as fixture_file:
            fixture_data = json.load(fixture_file)

        loaded_count = 0

        for item in fixture_data:
            tag_name = item["fields"]["name"]
            tag_type = item["fields"]["type"]

            # This will either get the existing tag or create a new one
            tag, created = Tag.objects.get_or_create(name=tag_name, type=tag_type)

            if created:
                loaded_count += 1

        if loaded_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully loaded {loaded_count} new tags")
            )
        else:
            self.stdout.write(self.style.NOTICE("All tags already exists."))
