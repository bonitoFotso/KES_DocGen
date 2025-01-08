from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Max
from django.utils.timezone import now
from django.core.exceptions import ValidationError



class Entity(models.Model):
    code = models.CharField(
        max_length=3,
        unique=True,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Client(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Site(models.Model):
    nom = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    localisation = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Category(models.Model):
    code = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )  # INS, FOR, QHS, etc.
    name = models.CharField(max_length=50)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    code = models.CharField(
        max_length=4,
        validators=[RegexValidator(regex='^(VTE|EC)\d+$')]
    )
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class DocumentStatus:
    DRAFT = 'BROUILLON'
    SENT = 'ENVOYE'
    VALIDATED = 'VALIDE'
    REJECTED = 'REFUSE'
    
    CHOICES = [
        (DRAFT, 'Brouillon'),
        (SENT, 'Envoyé'),
        (VALIDATED, 'Validé'),
        (REJECTED, 'Refusé'),
    ]

class DocumentType:
    OFFER = 'OFF'
    PROFORMA = 'PRO'
    BUSINESS = 'AFF'
    REPORT = 'RAP'
    INVOICE = 'FAC'
    CERTIFICATE = 'ATT'

class Document(models.Model):
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True, editable=False)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=DocumentStatus.CHOICES, default=DocumentStatus.DRAFT)
    doc_type = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )
    sequence_number = models.IntegerField(editable=False)

    class Meta:
        abstract = True

    def generate_reference(self):
        """Generate a unique reference number for the document."""
        if not self.sequence_number:
            self.sequence_number = self._get_next_sequence_number()
        
        date = self.date_creation or now()
        total_docs = self._get_total_documents() + 1
        
        reference_parts = [
            self.entity.code,
            self.doc_type,
            str(date.year),
            f"{date.month:02d}",
            str(self.client.id),
            str(total_docs),
            f"{self.sequence_number:04d}"
        ]
        
        return "-".join(reference_parts)

    def _get_next_sequence_number(self):
        """Get the next sequence number for the document type."""
        last_sequence = type(self).objects.filter(
            entity=self.entity,
            doc_type=self.doc_type,
            date_creation__year=now().year,
            date_creation__month=now().month
        ).aggregate(Max('sequence_number'))['sequence_number__max']
        return (last_sequence or 0) + 1

    def _get_total_documents(self):
        """Get the total number of documents for this client."""
        return type(self).objects.filter(client=self.client).count()

    def validate(self):
        """Validate the document and update its status."""
        if self.statut != DocumentStatus.VALIDATED:
            self.statut = DocumentStatus.VALIDATED
            self.date_validation = now()
            self.save()

    def clean(self):
        """Validate the document before saving."""
        super().clean()
        if self.statut == DocumentStatus.VALIDATED and not self.date_validation:
            raise ValidationError("A validated document must have a validation date.")

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

class Offre(Document):
    produit = models.ManyToManyField('Product')
    sites = models.ManyToManyField('Site')
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        
        if creating and self.statut == DocumentStatus.VALIDATED:
            self.create_proforma()

    def create_proforma(self):
        """Create a proforma when the offer is validated."""
        if self.statut != DocumentStatus.VALIDATED:
            raise ValidationError("Cannot create proforma for non-validated offer.")
            
        if hasattr(self, 'proforma'):
            return self.proforma
            
        return Proforma.objects.create(
            offre=self,
            client=self.client,
            entity=self.entity,
            doc_type=DocumentType.PROFORMA
        )

class Proforma(Document):
    offre = models.OneToOneField(Offre, on_delete=models.CASCADE, related_name="proforma")

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        
        if creating and self.statut == DocumentStatus.VALIDATED:
            self.create_business()

    def create_business(self):
        """Create a business case when the proforma is validated."""
        if self.statut != DocumentStatus.VALIDATED:
            raise ValidationError("Cannot create business case for non-validated proforma.")
            
        if hasattr(self, 'affaire'):
            return self.affaire
            
        return Affaire.objects.create(
            offre=self.offre,
            client=self.client,
            entity=self.entity,
            doc_type=DocumentType.BUSINESS
        )

class BusinessStatus:
    IN_PROGRESS = 'EN_COURS'
    COMPLETED = 'TERMINEE'
    CANCELLED = 'ANNULEE'
    
    CHOICES = [
        (IN_PROGRESS, 'En cours'),
        (COMPLETED, 'Terminée'),
        (CANCELLED, 'Annulée'),
    ]

class Affaire(Document):
    offre = models.OneToOneField(Offre, on_delete=models.CASCADE, related_name="affaire")
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin_prevue = models.DateTimeField(null=True, blank=True)
    statut_affaire = models.CharField(
        max_length=20,
        choices=BusinessStatus.CHOICES,
        default=BusinessStatus.IN_PROGRESS
    )

    def complete_business(self):
        """Complete the business case and generate related documents."""
        if self.statut_affaire != BusinessStatus.COMPLETED:
            raise ValidationError("Business case must be completed to generate documents.")
        
        self._create_reports()
        self._create_training_sessions()
        self._create_invoice()

    def _create_reports(self):
        """Create reports for each site and product combination."""
        for site in self.offre.sites.all():
            for produit in self.offre.produit.all():
                Rapport.objects.create(
                    affaire=self,
                    site=site,
                    produit=produit,
                    entity=self.entity,
                    doc_type=DocumentType.REPORT
                )

    def _create_training_sessions(self):
        """Create training sessions for training products."""
        for produit in self.offre.produit.filter(category__code='FOR'):
            Formation.objects.create(
                titre=f"Formation {produit.name}",
                client=self.client,
                affaire=self,
                date_debut=self.date_debut,
                date_fin=self.date_fin_prevue,
                description=f"Formation sur le produit {produit.name}"
            )

    def _create_invoice(self):
        """Create invoice for the business case."""
        return Facture.objects.create(
            affaire=self,
            client=self.client,
            entity=self.entity,
            doc_type=DocumentType.INVOICE
        )
class Facture(Document):
    affaire = models.OneToOneField(Affaire, on_delete=models.CASCADE, related_name="facture")

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = Facture.objects.filter(
                    entity=self.entity,
                    doc_type='FAC',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1
            total_factures_client = Facture.objects.filter(client=self.affaire.client).count() + 1
            date = self.date_creation or now()
            self.reference = f"{self.entity.code}-FAC-{self.affaire.id}-{self.affaire.offre.id}-{date.year}-{date.month:02d}-{self.client.id}-{total_factures_client}-{self.sequence_number:04d}"
        super().save(*args, **kwargs)


class Rapport(Document):
    affaire = models.ForeignKey(Affaire, on_delete=models.CASCADE, related_name="rapports")
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    produit = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="rapports")


    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = Rapport.objects.filter(
                    entity=self.entity,
                    doc_type='RAP',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1
            total_rapports_client = Rapport.objects.filter(client=self.affaire.client).count() + 1
            date = self.date_creation or now()
            self.reference = f"{self.entity.code}-RAP-{self.affaire.offre.id}-{self.affaire.offre.id}-{date.year}-{date.month:02d}-{self.client.id}-{total_rapports_client}-{self.sequence_number:04d}"
        super().save(*args, **kwargs)


class Formation(models.Model):
    titre = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="formations")
    affaire = models.ForeignKey(Affaire, on_delete=models.CASCADE, related_name="formations")
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, related_name="formation")
    date_debut = models.DateTimeField(blank=True, null=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titre} - {self.client.nom}"


class Participant(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    fonction = models.CharField(max_length=100, blank=True, null=True)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="participants")

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class AttestationFormation(Document):
    affaire = models.ForeignKey(Affaire, on_delete=models.CASCADE, related_name="attestations")
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="attestations")
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name= "attestation")
    details_formation = models.TextField()

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = AttestationFormation.objects.filter(
                    entity=self.entity,
                    client=self.affaire.client,
                    formation=self.formation,
                    doc_type='ATT',
                    date_creation__year=now().year,
                    date_creation__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1
            total_attestations_client = AttestationFormation.objects.filter(client=self.client).count() + 1
            date = self.date_creation or now()
            self.reference = f"{self.entity.code}-ATT-{self.affaire.id}-{date.year}-{date.month:02d}-{self.client.id}-{total_attestations_client}-{self.formation.id}-{self.participant.id}-{self.sequence_number:04d}"
        super().save(*args, **kwargs)


class DocumentPermission:
    pass