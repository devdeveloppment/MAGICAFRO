import os
import django
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product, ProductImage

# Mapping of product slugs to generated image paths
image_mapping = {
    'beurre-de-karite-brut': r'C:\Users\DENIS\.gemini\antigravity\brain\a3fc8364-9569-4665-b66c-c28fa733744e\beurre_karite_brut_1773185667118.png',
    'huile-davocat-pure': r'C:\Users\DENIS\.gemini\antigravity\brain\a3fc8364-9569-4665-b66c-c28fa733744e\huile_avocat_pure_1773185688071.png',
    'shampooing-solide-hibiscus': r'C:\Users\DENIS\.gemini\antigravity\brain\a3fc8364-9569-4665-b66c-c28fa733744e\shampooing_solide_hibiscus_1773185717660.png',
    'kit-de-pinceaux-bambou': r'C:\Users\DENIS\.gemini\antigravity\brain\a3fc8364-9569-4665-b66c-c28fa733744e\kit_pinceaux_bambou_1773185763634.png',
}

media_products_dir = os.path.join('media', 'products')
if not os.path.exists(media_products_dir):
    os.makedirs(media_products_dir)

for slug, src_path in image_mapping.items():
    try:
        product = Product.objects.get(slug=slug)
        filename = os.path.basename(src_path)
        dest_path = os.path.join(media_products_dir, filename)
        
        # Copy file
        shutil.copy2(src_path, dest_path)
        
        # Create ProductImage
        ProductImage.objects.create(
            product=product,
            image=f'products/{filename}',
            is_feature=True
        )
        print(f"Successfully added image for {slug}")
    except Product.DoesNotExist:
        print(f"Product with slug {slug} not found")
    except Exception as e:
        print(f"Error for {slug}: {e}")
