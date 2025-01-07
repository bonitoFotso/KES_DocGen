from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Max
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# Utilitaires
def generate_reference(entity_code, doc_type, related_ids, client_id, sequence):
    date = now()
    return f"{entity_code}-{doc_type}-{'-'.join(map(str, related_ids))}-{date.year}-{date.month:02d}-{client_id}-{sequence:04d}"


# Querysets personnalisés
class DocumentQuerySet(models.QuerySet):
    def with_related(self):
        return self.select_related('client', 'entity').prefetch_related('attachments')


# Modèles de base
class BaseModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Entity(BaseModel):
    code = models.CharField(
        max_length=3,
        unique=True,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Client(BaseModel):
    nom = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Site(BaseModel):
    nom = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    localisation = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Category(BaseModel):
    code = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )
    name = models.CharField(max_length=50)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(BaseModel):
    code = models.CharField(
        max_length=4,
        validators=[RegexValidator(regex='^(VTE|EC)\d+$')]
    )
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Gestion des documents
class DocumentStatus(models.TextChoices):
    DRAFT = 'BROUILLON', 'Brouillon'
    SENT = 'ENVOYE', 'Envoyé'
    VALIDATED = 'VALIDE', 'Validé'
    REFUSED = 'REFUSE', 'Refusé'


class Document(BaseModel):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    reference = models.CharField(max_length=50, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    doc_type = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )
    sequence_number = models.IntegerField()

    objects = DocumentQuerySet.as_manager()

    class Meta:
        abstract = False

    def __str__(self):
        return self.reference


class FinancialDocument(Document):
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        calculated_ttc = self.montant_ht + self.tva
        if abs(self.montant_ttc - calculated_ttc) > Decimal('0.01'):
            raise ValidationError("Le montant TTC doit être égal au montant HT + TVA")


class DocumentAttachment(BaseModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)


class DocumentVersion(BaseModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version = models.IntegerField()
    content = models.TextField()

    class Meta:
        unique_together = ['document', 'version']


class DocumentPermission(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='permissions')
    can_read = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_validate = models.BooleanField(default=False)


class DocumentNotification(BaseModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)


# Documents spécifiques
class Offre(FinancialDocument):
    produit = models.ManyToManyField(Product)
    date_modification = models.DateTimeField(auto_now=True)
    date_validation = models.DateTimeField(blank=True, null=True)
    sites = models.ManyToManyField(Site)

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = Offre.objects.filter(
                    entity=self.entity,
                    doc_type='OFF',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1

            self.reference = generate_reference(
                self.entity.code,
                'OFF',
                [],
                self.client.id,
                self.sequence_number
            )

        if self.statut == DocumentStatus.VALIDATED:
            self.date_validation = self.date_validation or now()
            self.creer_proforma()

        super().save(*args, **kwargs)

    def creer_proforma(self):
        if self.statut != DocumentStatus.VALIDATED:
            raise ValidationError("L'offre doit être validée pour créer un proforma.")

        if hasattr(self, 'proforma'):
            return self.proforma

        return Proforma.objects.create(
            offre=self,
            client=self.client,
            entity=self.entity,
            doc_type='PRO',
            montant_ht=self.montant_ht,
            montant_ttc=self.montant_ttc,
            tva=self.tva
        )


class Proforma(FinancialDocument):
    offre = models.OneToOneField(Offre, on_delete=models.CASCADE, related_name="proforma")

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = Proforma.objects.filter(
                    entity=self.entity,
                    doc_type='PRO',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1

            self.reference = generate_reference(
                self.entity.code,
                'PRO',
                [self.offre.id],
                self.client.id,
                self.sequence_number
            )

        if self.statut == DocumentStatus.VALIDATED:
            self.creer_affaire()

        super().save(*args, **kwargs)

    def creer_affaire(self):
        if self.statut != DocumentStatus.VALIDATED:
            raise ValidationError("Le proforma doit être validé pour créer une affaire.")

        if hasattr(self, 'affaire'):
            return self.affaire

        return Affaire.objects.create(
            proforma=self,
            client=self.client,
            entity=self.entity,
            doc_type='AFF'
        )


class Affaire(Document):
    proforma = models.OneToOneField(Proforma, on_delete=models.CASCADE, related_name="affaire")
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin_prevue = models.DateTimeField(null=True, blank=True)

    class AffaireStatus(models.TextChoices):
        EN_COURS = 'EN_COURS', 'En cours'
        TERMINEE = 'TERMINEE', 'Terminée'
        ANNULEE = 'ANNULEE', 'Annulée'

    statut_affaire = models.CharField(
        max_length=20,
        choices=AffaireStatus.choices,
        default=AffaireStatus.EN_COURS
    )

    def clean(self):
        super().clean()
        if self.date_fin_prevue and self.date_fin_prevue < self.date_debut:
            raise ValidationError("La date de fin prévue ne peut pas être antérieure à la date de début")

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = type(self).objects.filter(
                    entity=self.entity,
                    doc_type='AFF',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1

            self.reference = generate_reference(
                self.entity.code,
                'AFF',
                [self.proforma.offre.id],
                self.client.id,
                self.sequence_number
            )

        super().save(*args, **kwargs)


class Facture(FinancialDocument):
    affaire = models.OneToOneField(Affaire, on_delete=models.CASCADE, related_name="facture")

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = type(self).objects.filter(
                    entity=self.entity,
                    doc_type='FAC',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1

            self.reference = generate_reference(
                self.entity.code,
                'FAC',
                [self.affaire.id, self.affaire.proforma.offre.id],
                self.client.id,
                self.sequence_number
            )

        super().save(*args, **kwargs)


class Formation(BaseModel):
    titre = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="formations")
    proforma = models.OneToOneField(Proforma, on_delete=models.CASCADE, related_name="formation")
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def clean(self):
        super().clean()
        if self.date_fin < self.date_debut:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début")

    def __str__(self):
        return f"{self.titre} - {self.client.nom}"


class Participant(BaseModel):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    fonction = models.CharField(max_length=100, blank=True, null=True)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="participants")

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class AttestationFormation(Document):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="attestations")
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="attestation")
    details_formation = models.TextField()

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = type(self).objects.filter(
                    entity=self.entity,
                    doc_type='ATT',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1

            self.reference = generate_reference(
                self.entity.code,
                'ATT',
                [self.formation.proforma.affaire.id, self.formation.id, self.participant.id],
                self.client.id,
                self.sequence_number
            )

        super().save(*args, **kwargs)