from random import randint, randrange

from django.core.management import BaseCommand
from django.utils.text import slugify
from faker import Faker

from core.models import Category, Product, ProductImages, ProductVariation


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        faker = Faker("id_ID")
        categories = Category.objects.all()
        
        for i in range(80):
            seed = faker.uuid4()
            image_url = f"https://picsum.photos/seed/{seed}/600/400"  # Adjust dimensions as needed

            title = faker.catch_phrase()
            slug = slugify(title)
            
            product = Product.objects.create(
                title=title,
                slug=slug,
                description=faker.text(),
                price=randrange(200000, 500000),
                image=image_url,
                category=categories[i % len(categories)]
            )
            
            for _ in range(randint(1, 5)):
                ProductVariation.objects.create(
                    name=faker.safe_color_name(),
                    product=product
                )

            for _ in range(randint(1, 6)):
                ProductImages.objects.create(
                    name=image_url,
                    product=product
                )
                
        self.stdout.write(self.style.SUCCESS("🌱 Seeding has been completed"))