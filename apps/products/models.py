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
        if not self.slug:
            import uuid
            self.slug = f"cat-{str(uuid.uuid4())[:8]}"
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
    price = models.DecimalField(max_digits=12, decimal_places=2) # Increased max_digits for large FCFA values
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    badge = models.CharField(max_length=10, choices=BADGE_CHOICES, null=True, blank=True)
    rating_avg = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True, db_index=True)
    video = models.FileField(upload_to='products/videos/', null=True, blank=True)
    video_url = models.URLField(max_length=500, null=True, blank=True, help_text="Lien YouTube, TikTok, etc.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            import uuid
            self.slug = slugify(self.name)
            # Check if slug exists
            if Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{str(uuid.uuid4())[:4]}"
        if not self.slug:
            import uuid
            self.slug = f"prod-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)

    @property
    def get_primary_image(self):
        """Retourne l'URL de l'image principale du produit."""
        # Chercher d'abord les images prefetchées (optimisation)
        img = None
        if hasattr(self, 'feature_images') and self.feature_images:
            img = self.feature_images[0]
        else:
            img = self.images.filter(is_feature=True).first() or self.images.first()

        if img and img.image:
            try:
                url = img.image.url
                if url:
                    return url
            except Exception:
                pass

        # Fallback stable par ID (évite les changements visuels brusques)
        return f"https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=800&q=80&sig={self.id}"

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - (self.price / self.old_price)) * 100)
        return 0

    @property
    def get_video_embed_url(self):
        if not self.video_url:
            return None
        url = self.video_url
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return url

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_feature = models.BooleanField(default=False)

    @property
    def safe_image_url(self):
        """Return a reliable URL for the blog post image."""
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return "https://res.cloudinary.com/dtenc1xut/image/upload/v1/media/placeholder.png"

    @property
    def safe_url(self):
        """Return a reliable URL for the image.
        If the image exists (local or Cloudinary) return its URL.
        Otherwise return a placeholder hosted on Cloudinary.
        """
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return "https://res.cloudinary.com/dtenc1xut/image/upload/v1/media/placeholder.png"
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"

class Routine(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de la routine")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    discount_percentage = models.IntegerField(default=10, help_text="Pourcentage de réduction si achetée complète", verbose_name="Réduction (%)")
    image = models.ImageField(upload_to='routines/', null=True, blank=True, verbose_name="Image de couverture")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Routine Beauté"
        verbose_name_plural = "Routines Beauté"

    def save(self, *args, **kwargs):
        if not self.slug:
            import uuid
            self.slug = slugify(self.name)
            if Routine.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{str(uuid.uuid4())[:4]}"
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return sum(item.product.price for item in self.items.all())
    
    @property
    def discounted_price(self):
        return self.total_price * (100 - self.discount_percentage) / 100

    def __str__(self):
        return self.name

class RoutineItem(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    step_number = models.IntegerField(default=1, verbose_name="Numéro de l'étape")
    instructions = models.TextField(blank=True, help_text="Ex: Appliquer sur cheveux humides...", verbose_name="Instructions d'utilisation")

    class Meta:
        verbose_name = "Étape de Routine"
        verbose_name_plural = "Étapes de Routine"
        ordering = ['step_number']

    def __str__(self):
        return f"Étape {self.step_number} : {self.product.name} ({self.routine.name})"

class ReviewMedia(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='reviews/media/', verbose_name="Image ou Vidéo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Média d'Avis"
        verbose_name_plural = "Médias d'Avis"

    def __str__(self):
        return f"Média pour avis #{self.review.id}"
