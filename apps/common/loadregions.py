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
                title=region["name"],
                soato=region["soato"],
                title_uz=region["name_uz"],
                title_ru=region["name_ru"],
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Region {obj.title} created successfully"))
            else:
                self.stdout.write(self.style.WARNING(f"Region {obj.title} already exists"))

        for district in districts:
            region = Region.objects.get(soato=int(str(district["soato"])[:4]))
            obj, created = District.objects.get_or_create(
                title=district["name"],
                soato=district["soato"],
                region=region,
                title_uz=district["name_uz"],
                title_ru=district["name_ru"],
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"District {obj.title} created successfully"))
            else:
                self.stdout.write(self.style.WARNING(f"District {obj.title} already exists"))

        self.stdout.write(self.style.SUCCESS("Regions and districts loaded successfully!"))
