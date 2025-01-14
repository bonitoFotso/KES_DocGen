from django.db import models
from django.core.validators import RegexValidator

class Entity(models.Model):
    code = models.CharField(
        max_length=3,
        unique=True,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Entité"
        verbose_name_plural = "Entités"

    def __str__(self):
        return f"{self.code} - {self.name}"

class Client(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        indexes = [
            models.Index(fields=['nom']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.nom

    def get_full_address(self):
        return self.adresse or "Aucune adresse"

class Site(models.Model):
    nom = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sites')
    localisation = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        indexes = [
            models.Index(fields=['client', 'is_active']),
        ]

    def __str__(self):
        return f"{self.nom} - {self.client.nom}"

    def get_active_interventions(self):
        return self.interventions.filter(is_active=True)

class Category(models.Model):
    code = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )
    name = models.CharField(max_length=50)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="categories")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        unique_together = ['code', 'entity']
        indexes = [
            models.Index(fields=['code', 'entity']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

class Product(models.Model):
    code = models.CharField(
        max_length=4,
        validators=[RegexValidator(regex='^(VTE|EC)\d+$')]
    )
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="produits")
    description = models.TextField(blank=True, null=True)
    prix_standard = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        unique_together = ['code', 'category']
        indexes = [
            models.Index(fields=['code', 'category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_price_with_tax(self, tax_rate=0.20):
        return self.prix_standard * (1 + tax_rate)