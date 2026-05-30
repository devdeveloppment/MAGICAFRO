from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.city}"

class BeautyProfile(models.Model):
    HAIR_TYPE_CHOICES = [
        ('1', 'Lisse (1)'),
        ('2', 'Ondulé (2A, 2B, 2C)'),
        ('3', 'Bouclé (3A, 3B, 3C)'),
        ('4', 'Crépu (4A, 4B, 4C)'),
    ]
    POROSITY_CHOICES = [
        ('FAIBLE', 'Faible'),
        ('MOYENNE', 'Moyenne'),
        ('FORTE', 'Forte'),
    ]
    SKIN_TYPE_CHOICES = [
        ('SECHE', 'Sèche'),
        ('GRASSE', 'Grasse'),
        ('MIXTE', 'Mixte'),
        ('NORMALE', 'Normale'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='beauty_profile')
    hair_type = models.CharField(max_length=20, choices=HAIR_TYPE_CHOICES, blank=True, null=True, verbose_name="Type de cheveux")
    hair_porosity = models.CharField(max_length=20, choices=POROSITY_CHOICES, blank=True, null=True, verbose_name="Porosité")
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES, blank=True, null=True, verbose_name="Type de peau")
    primary_concern = models.CharField(max_length=255, blank=True, null=True, help_text="Ex: Hydratation, Pousse, Acné...", verbose_name="Préoccupation principale")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Beauté"
        verbose_name_plural = "Profils Beauté"

    def __str__(self):
        return f"Profil Beauté de {self.user.email}"
