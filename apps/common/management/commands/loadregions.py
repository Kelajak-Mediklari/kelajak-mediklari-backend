import json

from django.core.management.base import BaseCommand

from ...models import District, Region


class Command(BaseCommand):
    help = "Loads regions if they are not loaded"

    def handle(self, *args, **options):
        with open("data/regions.json", "r", encoding="UTF-8") as f:
            regions = json.load(f)

        with open("data/districts.json", "r", encoding="UTF-8") as f:
            districts = json.load(f)

        for region in regions:
            obj, created = Region.objects.get_or_create(
                name=region["name"]
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Region {obj.name} created successfully"))
            else:
                self.stdout.write(self.style.WARNING(f"Region {obj.name} already exists"))

        for district in districts:
            region = Region.objects.get(id=district['region_id'])
            obj, created = District.objects.get_or_create(
                name=district["name"],
                region=region
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"District {obj.name} created successfully"))
            else:
                self.stdout.write(self.style.WARNING(f"District {obj.name} already exists"))

        self.stdout.write(self.style.SUCCESS("Regions and districts loaded successfully!"))
