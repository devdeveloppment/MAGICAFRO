import os
from django.core.files import File
from products.models import Product, Category, ProductImage

cat_premium, _ = Category.objects.get_or_create(
    name='Édition Limitée', 
    slug='edition-limitee', 
    defaults={'icon': 'fa-crown'}
)

images_dir = r"C:\Users\DENIS\.gemini\antigravity\brain\a3fc8364-9569-4665-b66c-c28fa733744e"

data = [
    ('Soin Signature MagicAfro', 'soin-signature-magicafro', 'hero_woman_hair_touch_1773231294569.png', 45000, "L'excellence du soin capillaire pour une beauté sublimée."),
    ('Kit de Tressage Pro', 'kit-tressage-pro', 'woman_braiding_hair_1773231371852.png', 25000, "Tout ce qu'il vous faut pour des tresses parfaites et durables."),
    ('Masque Nutritif Intense', 'masque-nutritif-intense', 'applying_hair_product_1773231491698.png', 18500, "Nourrit en profondeur les boucles les plus assoiffées."),
    ("L'Huile d'Or Rare", 'huile-or-rare', 'premium_hair_oil_mockup_1773231641737.png', 55000, "Une huile précieuse aux extraits rares pour un éclat incomparable.")
]

for name, slug, fname, price, desc in data:
    prod, created = Product.objects.get_or_create(
        slug=slug, 
        defaults={
            'name': name,
            'category': cat_premium,
            'price': price,
            'description': desc,
            'is_active': True
        }
    )
    if not prod.images.exists():
        fpath = os.path.join(images_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, 'rb') as f:
                ProductImage.objects.create(
                    product=prod,
                    image=File(f, name=fname),
                    is_feature=True
                )
            print(f"Image {fname} for {prod.name} successfully linked.")
        else:
            print(f"Image {fpath} not found.")
    else:
        print(f"Product {prod.name} already has images.")
