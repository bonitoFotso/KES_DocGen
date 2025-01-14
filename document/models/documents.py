from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from document.models import Affaire
from .base import DocumentBase, BaseState, ValidationMixin, WorkflowMixin, OptimizedQuerySetMixin, AffaireState

class Offre(DocumentBase, WorkflowMixin, ValidationMixin, OptimizedQuerySetMixin):
    reference_pattern = "{entity}-OFF-{year}-{month:02d}-{client}-{count}-{seq:04d}"
    
    produit = models.ManyToManyField('Product', related_name='offres')
    date_modification = models.DateTimeField(auto_now=True)
    sites = models.ManyToManyField('Site', related_name='offres')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commentaires = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Offre"
        verbose_name_plural = "Offres"
        indexes = [
            models.Index(fields=['statut', 'date_creation']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            total_offres_client = Offre.objects.filter(client=self.client).count() + 1
            self.reference = self.generate_reference(client=self.client.id, count=total_offres_client)

        if self.statut == BaseState.VALIDE and not self.date_validation:
            self.date_validation = now()
            self.creer_proforma()

        super().save(*args, **kwargs)

    def creer_proforma(self):
        if self.statut != BaseState.VALIDE:
            raise ValueError("L'offre doit être validée pour créer un proforma")

        if hasattr(self, 'proforma'):
            raise ValueError("Un proforma existe déjà pour cette offre")

        return Proforma.objects.create(
            offre=self,
            client=self.client,
            entity=self.entity,
            doc_type='PRO',
            montant_total=self.montant_total
        )

    def calculate_total(self):
        self.montant_total = sum(produit.prix_standard for produit in self.produit.all())
        self.save()

    def validate_products(self):
        if not self.produit.exists():
            raise ValidationError("L'offre doit contenir au moins un produit")

class Proforma(DocumentBase, WorkflowMixin, ValidationMixin, OptimizedQuerySetMixin):
    reference_pattern = "{entity}-PRO-{offre}-{year}-{month:02d}-{client}-{count}-{seq:04d}"
    
    offre = models.OneToOneField(Offre, on_delete=models.CASCADE, related_name="proforma")
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conditions_paiement = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Proforma"
        verbose_name_plural = "Proformas"
        indexes = [
            models.Index(fields=['statut', 'date_creation']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            total_proformas_client = Proforma.objects.filter(client=self.client).count() + 1
            self.reference = self.generate_reference(
                client=self.client.id,
                count=total_proformas_client,
                offre=self.offre.id
            )

        if self.statut == BaseState.VALIDE and not self.date_validation:
            self.date_validation = now()
            self.creer_affaire()

        super().save(*args, **kwargs)

    def creer_affaire(self):
        """
        Crée l'affaire associée au proforma une fois validé
        """
        if self.statut != BaseState.VALIDE:
            raise ValidationError("Le proforma doit être validé pour créer une affaire")

        if hasattr(self, 'affaire'):
            raise ValidationError("Une affaire existe déjà pour ce proforma")

        if not self.date_validation:
            raise ValidationError("Le proforma n'a pas de date de validation")

        return Affaire.objects.create(
            offre=self.offre,
            client=self.client,
            entity=self.entity,
            doc_type='AFF',
            montant_final=self.montant_total
        )
    def clean(self):
        super().clean()
        if self.montant_total <= 0:
            raise ValidationError("Le montant total doit être supérieur à 0")