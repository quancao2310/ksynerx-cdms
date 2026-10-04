from apps.products.models import Category, Product
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from faker_ecommerce import EcommerceProvider

ASSET_TYPES = ["Single", "Bundle", "MultipleBarcodes"]
UNITS = ["Cái", "Hộp", "Thùng", "Chai", "Gói", "Bộ", "Kg", "Lốc"]
SIZES = ["XS", "S", "M", "L", "XL", "XXL", "One Size"]


class Command(BaseCommand):
    help = "Seed Category and Product data."

    def add_arguments(self, parser):
        parser.add_argument("--categories", type=int, default=20)
        parser.add_argument("--products", type=int, default=1000)
        parser.add_argument("--clear", action="store_true", help="Delete existing data")

    @transaction.atomic
    def handle(self, *args, **kwargs):
        fake = Faker()
        fake.add_provider(EcommerceProvider)

        if kwargs["clear"]:
            Category.objects.all().delete()
            Product.objects.all().delete()
            self.stdout.write("Cleared existing data.")

        categories = self._create_categories(fake, kwargs["categories"])
        products = self._create_products(
            fake=fake,
            categories=categories,
            count=kwargs["products"],
        )

        self.stdout.write(self.style.SUCCESS(
            f"Done: {len(categories)} categories total, {len(products)} products created"
        ))

    def _create_categories(self, fake, count):
        existing_codes = set(Category.objects.values_list("code", flat=True))
        new = []
        while len(new) < count:
            code = fake.bothify("CAT-????-##").upper()
            if code in existing_codes:
                continue
            existing_codes.add(code)
            new.append(Category(code=code, name=fake.product_category()))
        Category.objects.bulk_create(new)
        return list(Category.objects.all())

    def _create_products(self, fake, categories, count):
        # Create products
        existing_skus = set(Product.objects.values_list("sku", flat=True))
        products = []
        for _ in range(count):
            while True:
                sku = fake.sku()
                if sku not in existing_skus:
                    existing_skus.add(sku)
                    break

            products.append(
                Product(
                    name=fake.product_name(),
                    description=fake.product_description() if fake.boolean(80) else None,
                    sku=sku,
                    partner_sku=f"P-{sku}" if fake.boolean(60) else None,
                    asset_type=fake.random_element(ASSET_TYPES),
                    has_serial=fake.boolean(20),
                    has_expiration=fake.boolean(30),
                    color=fake.safe_color_name() if fake.boolean(50) else None,
                    size=fake.random_element(SIZES) if fake.boolean(40) else None,
                    is_active=fake.boolean(90),
                    units=fake.random_elements(elements=UNITS, length=fake.random_int(1, 3), unique=True),
                )
            )

        created = Product.objects.bulk_create(products, batch_size=1000)

        # Create M2M links
        Through = Product.categories.through
        links = []
        max_k = min(3, len(categories))
        for product in created:
            picked = fake.random_elements(elements=categories, length=fake.random_int(1, max_k), unique=True)
            links.extend(Through(product_id=product.pk, category_id=c.pk) for c in picked)
        Through.objects.bulk_create(links, batch_size=1000)

        return created
