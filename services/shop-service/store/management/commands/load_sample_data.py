from django.core.management.base import BaseCommand
from store.models import Product, Category


class Command(BaseCommand):
    help = "Загружает тестовые товары и категории в БД"

    def handle(self, *args, **options):
        self.stdout.write("Загрузка тестовых данных...")

        # Создаем две категории с разными переменными
        smartphones_category, sm_created = Category.objects.get_or_create(name="Смартфоны")
        laptops_category, lp_created = Category.objects.get_or_create(name="Ноутбуки")

        if sm_created:
            self.stdout.write(self.style.SUCCESS(f"Категория создана: {smartphones_category.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Категория существует: {smartphones_category.name}"))

        if lp_created:
            self.stdout.write(self.style.SUCCESS(f"Категория создана: {laptops_category.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Категория существует: {laptops_category.name}"))

        # Товары с указанием категории для каждого
        products_data = [
            {"name": "iPhone 15", "description": "Флагманский смартфон", "price": 120000.00, "category": smartphones_category},
            {"name": "Samsung Galaxy S24", "description": "Смартфон с ИИ-камерой", "price": 95000.00, "category": smartphones_category},
            {"name": "Xiaomi 13 Ultra", "description": "Фотографский смартфон", "price": 75000.00, "category": smartphones_category},
            {"name": "Google Pixel 8 Pro", "description": "Лучшая камера", "price": 85000.00, "category": smartphones_category},
            {"name": "MacBook Pro 16", "description": "Профессиональный ноутбук", "price": 250000.00, "category": laptops_category},
            {"name": "Dell XPS 15", "description": "Ноутбук для дизайнеров", "price": 180000.00, "category": laptops_category},
        ]

        created_count = 0
        for data in products_data:
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "price": data["price"],
                    "category": data["category"]
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f"Товар создан: {product.name} - {product.price} руб. ({product.category.name})")
            else:
                self.stdout.write(f"Товар существует: {product.name}")

        self.stdout.write(self.style.SUCCESS("\nЗагрузка завершена"))
        self.stdout.write(f"Категорий: {Category.objects.count()}")
        self.stdout.write(f"Товаров: {Product.objects.count()}")
        self.stdout.write(f"Создано сейчас: {created_count}")