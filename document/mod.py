from django.db import models
from django.db.models import Max
from django.utils.timezone import now
from django.core.validators import RegexValidator


class Client(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Entity:
    pass

class DocumentType(models.Model):
    code = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )  # PRF, FAC, etc.
    name = models.CharField(max_length=50)
    reset_frequency = models.CharField(
        choices=[('YEARLY', 'Yearly'), ('MONTHLY', 'Monthly'), ('NEVER', 'Never')],
        max_length=10
    )

    def __str__(self):
        return self.name

class Document(models.Model):
    STATUTS = [
        ('BROUILLON', 'Brouillon'),
        ('ENVOYE', 'Envoyé'),
        ('VALIDE', 'Validé'),
        ('REFUSE', 'Refusé'),
    ]
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    reference = models.CharField(max_length=50, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="documents")
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=STATUTS, default='BROUILLON')
    doc_type = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex='^[A-Z]{3}$')]
    )  # PRF, FAC, etc.
    sequence_number = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.reference


class Site:
    pass


class Category:
    pass


class Product:
    pass


class Offre(Document):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_modification = models.DateTimeField(auto_now=True)
    date_validation = models.DateTimeField(blank=True, null=True)  # Date d'acceptation
    sites = models.ManyToManyField(Site)

    def valider(self):
        """Créer un Proforma à partir de cette Offre."""
        if self.statut != 'VALIDE':
            raise ValueError("L'offre doit être validée avant de générer un Proforma.")
        return Proforma.objects.create(offre=self, client=self.client)

    def save(self, *args, **kwargs):
        # Génération du numéro unique
        if not self.reference:
            if not self.sequence_number:
                last_sequence = Document.objects.filter(
                    entity=self.entity,
                    doc_type='OFF',
                    category=self.category,
                    product=self.product,
                    created_date__year=now().year,
                    created_date__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1
            total_offres_Client = Offre.objects.filter(
                client = self.client
            ).count() + 1
            if not self.date_creation:
                from datetime import datetime
                date = datetime.now()
            else:
                date = self.date_creation
            self.reference = f"{self.entity.code}-OFF-{self.category.code}-{self.product.code}-{date.year}-{date.month:02d}-{total_offres_Client}-{self.sequence_number:04d}"

        # Si l'offre est acceptée, enregistrer la date de validation
        if self.statut == 'VALIDE' and not self.date_validation:
            self.date_validation = now()

        super().save(*args, **kwargs)


class Proforma(Document):
    offre = models.OneToOneField(Offre, on_delete=models.CASCADE, related_name="proforma")

    def valider(self):
        """Créer un Rapport, Facture ou Attestation Formation."""
        if self.statut != 'VALIDE':
            raise ValueError("Le Proforma doit être validé avant de générer un document final.")
        documents = []
        if "formation" in self.offre.produits.lower():
            formation = Formation.objects.create(client=self.client, proforma=self)
            documents.append(AttestationFormation.objects.create(proforma=self, formation=formation, client=self.client))
            documents.append(Facture.objects.create(proforma=self, client=self.client))
            documents.append(Rapport.objects.create(proforma=self, client=self.client))
        else:
            documents.append(Facture.objects.create(proforma=self, client=self.client))
            documents.append(Rapport.objects.create(proforma=self, client=self.client))
        return documents

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = Document.objects.filter(
                    entity=self.entity,
                    doc_type=self.doc_type,
                    category=self.offre.category,
                    product=self.offre.product,
                    created_date__year=now().year,
                    created_date__month=now().month
                ).aggregate(Max('sequence_number'))['sequence_number__max']
                self.sequence_number = (last_sequence or 0) + 1
            total_Proformat_Client = Offre.objects.filter(
                client=self.offre.client
            ).count() + 1
            if not self.date_creation:
                from datetime import datetime
                date = datetime.now()
            else:
                date = self.date_creation
            self.numero = f"{self.offre.entity.code}-PRO-{self.offre.category.code}-{self.offre.product.code}-{date.year}-{date.month:02d}-{total_Proformat_Client}-{self.sequence_number:04d}"
        super().save(*args, **kwargs)


class Facture(Document):
    proforma = models.OneToOneField(Proforma, on_delete=models.CASCADE, related_name="facture")


class Rapport(Document):
    proforma = models.OneToOneField(Proforma, on_delete=models.CASCADE, related_name="rapport")


class Formation(models.Model):
    titre = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="formations")
    proforma = models.OneToOneField(Proforma, on_delete=models.CASCADE, related_name="formation")
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
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
    proforma = models.OneToOneField(Proforma, on_delete=models.CASCADE, related_name="attestation")
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="attestations")
    details_formation = models.TextField()
