import json
from django.core.management.base import BaseCommand
from products.models import Category, Product

class Command(BaseCommand):
    help = 'Import products from JSON file'

    def handle(self, *args, **options):
        with open(r'C:\Users\Arbin Sigdel\Dropbox\PC\Desktop\ML Task\Aakash Groups\ecommerce_recommender\products.json', 'r') as f:
            data = json.load(f)
        
        for category_name, products in data.items():
            category, created = Category.objects.get_or_create(name=category_name)
            
            for product_data in products:
                Product.objects.get_or_create(
                    category=category,
                    name=product_data['name'],
                    defaults={
                        'description': product_data['description'],
                        'price': product_data['price']
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully imported products'))