from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    icon = models.CharField(max_length=100, blank=True, help_text="FontAwesome icon class")
    order = models.IntegerField(default=0)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    BADGE_CHOICES = [
        ('NEW', 'Nouveau'),
        ('PROMO', 'Promo'),
        ('BEST', 'Bestseller'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    badge = models.CharField(max_length=10, choices=BADGE_CHOICES, null=True, blank=True)
    rating_avg = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_primary_image(self):
        img = self.images.filter(is_feature=True).first()
        if not img:
            img = self.images.first()
        
        if img:
            return img.image.url
            
        # Fallback beauty images to keep the UI premium even without content
        fallbacks = [
            'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=400&auto=format&fit=crop', # Serum
            'https://images.unsplash.com/photo-1596462502278-27bfaf41039a?q=80&w=400&auto=format&fit=crop', # Cream
            'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?q=80&w=400&auto=format&fit=crop', # Oil
            'https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=400&auto=format&fit=crop', # Soap
        ]
        import zlib
        # Use name to pick a stable fallback per product
        idx = zlib.adler32(self.name.encode()) % len(fallbacks)
        return fallbacks[idx]

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - (self.price / self.old_price)) * 100)
        return 0

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_feature = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"
