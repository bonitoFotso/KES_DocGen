from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from .base import (
    DocumentBase, 
    BaseState, 
    ValidationMixin, 
    WorkflowMixin, 
    OptimizedQuerySetMixin, 
    AffaireState
)

class Affaire(DocumentBase, WorkflowMixin, ValidationMixin, OptimizedQuerySetMixin):
    reference_pattern = "{entity}-AFF-{offre}-{year}-{month:02d}-{client}-{count}-{seq:04d}"
    
    offre = models.OneToOneField('Offre', on_delete=models.CASCADE, related_name="affaire")
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin_prevue = models.DateTimeField(null=True, blank=True)
    date_fin_reelle = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=AffaireState.choices,
        default=AffaireState.EN_COURS
    )
    responsable = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='affaires_gerees'
    )
    montant_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commentaires = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Affaire"
        verbose_name_plural = "Affaires"
        indexes = [
            models.Index(fields=['statut', 'date_debut']),
            models.Index(fields=['responsable']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            if not self.sequence_number:
                last_sequence = self.__class__.objects.get_next_sequence(
                    self.entity,
                    self.doc_type,
                    now().year,
                    now().month
                )
                self.sequence_number = last_sequence
            
            total_affaires_client = Affaire.objects.filter(client=self.client).count() + 1
            self.reference = self.generate_reference(
                client=self.client.id,
                count=total_affaires_client,
                offre=self.offre.id
            )

        # Mise à jour automatique du montant final depuis l'offre si non défini
        if not self.montant_final and self.offre:
            self.montant_final = self.offre.montant_total

        if self.statut == AffaireState.TERMINEE and not self.date_fin_reelle:
            self.date_fin_reelle = now()
            self.creer_facture()
            self.creer_rapports()

        super().save(*args, **kwargs)

    def creer_facture(self):
        """Crée la facture associée à l'affaire"""
        if self.statut != AffaireState.TERMINEE:
            raise ValidationError("L'affaire doit être terminée pour créer une facture")

        if hasattr(self, 'facture'):
            raise ValidationError("Une facture existe déjà pour cette affaire")

        return Facture.objects.create(
            affaire=self,
            client=self.client,
            entity=self.entity,
            doc_type='FAC',
            montant_total=self.montant_final
        )

    def creer_rapports(self):
        """Crée les rapports associés à l'affaire"""
        if self.statut != AffaireState.TERMINEE:
            raise ValidationError("L'affaire doit être terminée pour créer les rapports")
        
        rapports_crees = []
        # Création des rapports pour chaque combinaison site/produit
        for site in self.offre.sites.all():
            for produit in self.offre.produit.all():
                rapport = Rapport.objects.create(
                    affaire=self,
                    site=site,
                    produit=produit,
                    client=self.client,
                    entity=self.entity,
                    doc_type='RAP'
                )
                rapports_crees.append(rapport)

                # Si c'est un produit de formation, créer une formation
                if produit.category.code == 'FOR':
                    formation = Formation.objects.create(
                        titre=f"Formation {produit.name}",
                        client=self.client,
                        affaire=self,
                        rapport=rapport,
                        date_debut=self.date_debut,
                        date_fin=self.date_fin_reelle or self.date_fin_prevue,
                        description=f"Formation sur {produit.name}"
                    )
                    
        return rapports_crees

class Facture(DocumentBase, WorkflowMixin, ValidationMixin, OptimizedQuerySetMixin):
    reference_pattern = "{entity}-FAC-{affaire}-{year}-{month:02d}-{client}-{count}-{seq:04d}"
    
    affaire = models.OneToOneField(Affaire, on_delete=models.CASCADE, related_name="facture")
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_echeance = models.DateField(null=True, blank=True)
    conditions_paiement = models.TextField(blank=True, null=True)
    est_payee = models.BooleanField(default=False)
    date_paiement = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        indexes = [
            models.Index(fields=['est_payee', 'date_echeance']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            total_factures_client = Facture.objects.filter(client=self.client).count() + 1
            self.reference = self.generate_reference(
                client=self.client.id,
                count=total_factures_client,
                affaire=self.affaire.id
            )
        super().save(*args, **kwargs)

    def marquer_comme_payee(self, date_paiement=None):
        self.est_payee = True
        self.date_paiement = date_paiement or now().date()
        self.save()

class Rapport(DocumentBase, WorkflowMixin, ValidationMixin, OptimizedQuerySetMixin):
    reference_pattern = "{entity}-RAP-{affaire}-{year}-{month:02d}-{client}-{count}-{seq:04d}"
    
    affaire = models.ForeignKey(Affaire, on_delete=models.CASCADE, related_name="rapports")
    site = models.ForeignKey('Site', on_delete=models.CASCADE, related_name="rapports")
    produit = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="rapports")
    contenu = models.TextField(blank=True, null=True)
    date_intervention = models.DateField(null=True, blank=True)
    intervenant = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='rapports_realises'
    )

    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        unique_together = ['affaire', 'site', 'produit']
        indexes = [
            models.Index(fields=['date_intervention']),
            models.Index(fields=['intervenant']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            total_rapports_client = Rapport.objects.filter(client=self.client).count() + 1
            self.reference = self.generate_reference(
                client=self.client.id,
                count=total_rapports_client,
                affaire=self.affaire.id
            )
        super().save(*args, **kwargs)

class Formation(models.Model):
    titre = models.CharField(max_length=255)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name="formations")
    affaire = models.ForeignKey(Affaire, on_delete=models.CASCADE, related_name="formations")
    rapport = models.OneToOneField(Rapport, on_delete=models.CASCADE, related_name="formation")
    formateur = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='formations_donnees'
    )
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    objectifs = models.TextField(blank=True, null=True)
    prerequis = models.TextField(blank=True, null=True)
    materiel_necessaire = models.TextField(blank=True, null=True)
    evaluation_moyenne = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        indexes = [
            models.Index(fields=['date_debut', 'date_fin']),
            models.Index(fields=['formateur']),
        ]

    def __str__(self):
        return f"{self.titre} - {self.client.nom}"

    def clean(self):
        super().clean()
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début")

    def calculate_duration(self):
        """Calcule la durée de la formation en heures"""
        if self.date_debut and self.date_fin:
            duration = self.date_fin - self.date_debut
            return duration.total_seconds() / 3600
        return 0

    def update_evaluation_moyenne(self):
        """Met à jour la note moyenne de la formation"""
        evaluations = self.evaluations.all()
        if evaluations:
            moyenne = sum(eval.note for eval in evaluations) / len(evaluations)
            self.evaluation_moyenne = round(moyenne, 2)
            self.save()

class Participant(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    fonction = models.CharField(max_length=100, blank=True, null=True)
    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="participants"
    )
    present = models.BooleanField(default=True)
    note_evaluation = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    commentaire_evaluation = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Participant"
        verbose_name_plural = "Participants"
        unique_together = ['email', 'formation']
        indexes = [
            models.Index(fields=['nom', 'prenom']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Met à jour la moyenne de la formation si une note est donnée
        if self.note_evaluation:
            self.formation.update_evaluation_moyenne()

class AttestationFormation(DocumentBase, WorkflowMixin, ValidationMixin, OptimizedQuerySetMixin):
    reference_pattern = "{entity}-ATT-{formation}-{year}-{month:02d}-{participant}-{seq:04d}"
    
    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="attestations"
    )
    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE,
        related_name="attestation"
    )
    details_formation = models.TextField()
    date_emission = models.DateField(auto_now_add=True)
    competences_acquises = models.TextField(blank=True, null=True)
    resultat_evaluation = models.TextField(blank=True, null=True)
    signature_formateur = models.BooleanField(default=False)
    signature_participant = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Attestation de formation"
        verbose_name_plural = "Attestations de formation"
        indexes = [
            models.Index(fields=['date_emission']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            total_attestations = AttestationFormation.objects.filter(
                formation=self.formation
            ).count() + 1
            self.reference = self.generate_reference(
                formation=self.formation.id,
                participant=self.participant.id,
                seq=total_attestations
            )
        super().save(*args, **kwargs)

    def is_complete(self):
        """Vérifie si l'attestation est complète"""
        return (
            self.signature_formateur and 
            self.signature_participant and 
            self.competences_acquises and 
            self.resultat_evaluation
        )