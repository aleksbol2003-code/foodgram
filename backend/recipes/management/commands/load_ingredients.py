import json
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импорт ингредиентов из JSON"

    def handle(self, *args, **options):
        path = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "ingredients.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data:
            Ingredient.objects.get_or_create(
                name=item["name"],
                defaults={"measurement_unit": item["measurement_unit"]},
            )
        self.stdout.write(self.style.SUCCESS(f"Загружено {Ingredient.objects.count()} ингредиентов"))
