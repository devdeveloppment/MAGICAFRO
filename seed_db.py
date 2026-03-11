import os
import django
import sys
from django.utils.text import slugify

# Add the project root and apps to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Category, Product, ProductImage
from marketing.models import Testimonial
from django.core.files.base import ContentFile
import requests

def seed_data():
    print("Seeding data...")
    
    # Categories
    categories = [
        {'name': 'Shampooings', 'icon': 'fa-soap', 'order': 1},
        {'name': 'Masques', 'icon': 'fa-mask', 'order': 2},
        {'name': 'Huiles', 'icon': 'fa-droplet', 'order': 3},
        {'name': 'Beurres', 'icon': 'fa-jar', 'order': 4},
        {'name': 'Maquillage', 'icon': 'fa-brush', 'order': 5},
        {'name': 'Accessoires', 'icon': 'fa-hat-wizard', 'order': 6},
    ]
    
    cat_objs = []
    for cat in categories:
        obj, created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={'icon': cat['icon'], 'order': cat['order']}
        )
        cat_objs.append(obj)
        print(f"Category {obj.name} ready.")

    # Products
    products = [
        {
            'name': 'Beurre de Karité Brut',
            'price': 24.90,
            'old_price': 29.90,
            'category': cat_objs[3],
            'badge': 'BEST',
            'desc': 'Hydratant et nourrissant peaux & cheveux. 100% naturel.'
        },
        {
            'name': 'Huile d\'Avocat Pure',
            'price': 15.90,
            'old_price': 19.90,
            'category': cat_objs[2],
            'badge': 'PROMO',
            'desc': 'Stimule la pousse et fortifie.'
        },
        {
            'name': 'Shampooing Solide Hibiscus',
            'price': 12.50,
            'old_price': None,
            'category': cat_objs[0],
            'badge': 'NEW',
            'desc': 'Cheveux ternes et fatigués.'
        },
        {
            'name': 'Kit de Pinceaux Bambou',
            'price': 39.00,
            'old_price': None,
            'category': cat_objs[5],
            'badge': 'NEW',
            'desc': 'Application douce et précise.'
        },
    ]
    
    for p in products:
        prod, created = Product.objects.get_or_create(
            name=p['name'],
            defaults={
                'price': p['price'],
                'old_price': p['old_price'],
                'category': p['category'],
                'badge': p['badge'],
                'description': p['desc'],
                'rating_avg': 4.9,
                'stock': 50
            }
        )
        print(f"Product {prod.name} ready.")

    # Testimonials
    testimonials = [
        {'name': 'Aminata K.', 'city': 'Paris', 'comment': 'Enfin des produits qui comprennent vraiment les besoins des cheveux crépus. Mon beurre de karité est magique !'},
        {'name': 'Sarah M.', 'city': 'Lyon', 'comment': 'L\'huile d\'avocat a transformé ma routine. Mes cheveux sont plus souples et brillants. Livraison super rapide.'},
        {'name': 'Léa D.', 'city': 'Marseille', 'comment': 'Superbe sélection de soins bio. Le site est magnifique et les conseils sont au top. Je recommande à 100%.'},
    ]
    
    for t in testimonials:
        Testimonial.objects.get_or_create(
            name=t['name'],
            defaults={'city': t['city'], 'comment': t['comment'], 'rating': 5}
        )
        print(f"Testimonial from {t['name']} ready.")

    print("Seeding complete!")

if __name__ == '__main__':
    seed_data()
