from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    image = models.ImageField(upload_to='blog/', null=True, blank=True)
    @property
    def safe_image_url(self):
        """Return a reliable URL for the blog post image, falling back to a placeholder if missing."""
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return "https://res.cloudinary.com/dtenc1xut/image/upload/v1/media/placeholder.png"
    video = models.FileField(upload_to='blog/videos/', null=True, blank=True)
    video_url = models.URLField(max_length=500, null=True, blank=True, help_text="Lien YouTube, TikTok, etc.")
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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
        return self.title
