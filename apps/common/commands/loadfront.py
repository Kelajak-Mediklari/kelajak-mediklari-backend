import json

from django.core.management.base import BaseCommand

from apps.common.utils import bulk_import_translations


class Command(BaseCommand):
    help = "Import frontend translates from json. "

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED("In proccess... wait... ru"))
        
        # Load Russian translations
        with open("data/front_ru.json") as json_file_ru:
            data_ru = json.load(json_file_ru)
        
        # Convert to the format expected by bulk_import_translations
        ru_translations = {
            key: {'text_ru': value} 
            for key, value in data_ru.items() 
            if isinstance(value, str)
        }
        
        ru_stats = bulk_import_translations(ru_translations)
        self.stdout.write(
            self.style.SUCCESS(
                f"Russian translations: {ru_stats['created']} created, {ru_stats['updated']} updated"
            )
        )
        
        self.stdout.write(self.style.HTTP_NOT_MODIFIED("In proccess... wait...uz"))
        
        # Load Uzbek translations
        with open("data/front_uz.json") as json_file_uz:
            data_uz = json.load(json_file_uz)
        
        # Convert to the format expected by bulk_import_translations
        uz_translations = {
            key: {'text_uz': value} 
            for key, value in data_uz.items() 
            if isinstance(value, str)
        }
        
        uz_stats = bulk_import_translations(uz_translations)
        self.stdout.write(
            self.style.SUCCESS(
                f"Uzbek translations: {uz_stats['created']} created, {uz_stats['updated']} updated"
            )
        )
        
        total_created = ru_stats['created'] + uz_stats['created']
        total_updated = ru_stats['updated'] + uz_stats['updated']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Total: {total_created} created, {total_updated} updated"
            )
        )
        self.stdout.write(self.style.SUCCESS("Successfully imported all translations"))
