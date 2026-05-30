import os, sys, django
sys.path.insert(0, 'apps')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from products.models import ProductImage, Product
from django.db.models import Count

print("=== ProductImages en DB ===")
for pi in ProductImage.objects.select_related('product').all():
    print(f"  ID={pi.id} | Product={pi.product.name} | field='{pi.image}' | feature={pi.is_feature}")
    try:
        print(f"    URL: {pi.image.url}")
    except Exception as e:
        print(f"    URL ERROR: {e}")

print()
print("=== Produits sans image ===")
prods_no_img = Product.objects.annotate(img_count=Count('images')).filter(img_count=0)
for p in prods_no_img:
    print(f"  - {p.name} (slug={p.slug}, id={p.id})")

print()
print("=== Tous les produits ===")
for p in Product.objects.annotate(img_count=Count('images')):
    print(f"  - {p.name} | images={p.img_count} | slug={p.slug}")
