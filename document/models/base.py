from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseState(models.TextChoices):
    BROUILLON = 'BROUILLON', 'Brouillon'
    ENVOYE = 'ENVOYE', 'Envoyé'
    VALIDE = 'VALIDE', 'Validé'
    REFUSE = 'REFUSE', 'Refusé'
    TERMINE = 'TERMINE', 'Terminé'

class AffaireState(models.TextChoices):
    EN_COURS = 'EN_COURS', 'En cours'
    TERMINEE = 'TERMINEE', 'Terminée'
    ANNULEE = 'ANNULEE', 'Annulée'

class DocumentHistory(models.Model):
    """
    Modèle pour tracer l'historique des changements de statut des documents
    """
    document_type = models.CharField(max_length=50)
    document_id = models.IntegerField()
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['document_type', 'document_id']),
        ]

class DocumentManager(models.Manager):
    def get_next_sequence(self, entity, doc_type, year, month):
        """
        Obtient le prochain numéro de séquence pour un type de document
        """
        return self.filter(
            entity=entity,
            doc_type=doc_type,
            date_creation__year=year,
            date_creation__month=month
        ).aggregate(models.Max('sequence_number'))['sequence_number__max'] or 0 + 1

class ValidationMixin:
    """
    Mixin pour ajouter des validations communes
    """
    def clean(self):
        super().clean()
        if hasattr(self, 'date_fin') and hasattr(self, 'date_debut'):
            if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
                raise ValidationError("La date de fin ne peut pas être antérieure à la date de début")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class WorkflowMixin:
    """
    Mixin pour la gestion des transitions d'état
    """
    def next_state(self):
        """Détermine les prochains états possibles"""
        state_transitions = {
            BaseState.BROUILLON: [BaseState.ENVOYE],
            BaseState.ENVOYE: [BaseState.VALIDE, BaseState.REFUSE],
            BaseState.REFUSE: [BaseState.BROUILLON],
            BaseState.VALIDE: [BaseState.TERMINE],
        }
        return state_transitions.get(self.statut, [])

    def can_transition_to(self, new_state):
        return new_state in self.next_state()

    def transition_to(self, new_state, user=None, comment=None):
        if not self.can_transition_to(new_state):
            raise ValueError(f"Transition impossible de {self.statut} vers {new_state}")
            
        old_status = self.statut
        self.statut = new_state
        self.save()
        
        DocumentHistory.objects.create(
            document_type=self.__class__.__name__,
            document_id=self.id,
            old_status=old_status,
            new_status=new_state,
            changed_by=user,
            comment=comment
        )

class OptimizedQuerySetMixin:
    """
    Mixin pour l'optimisation des requêtes
    """
    @classmethod
    def get_related_fields(cls):
        return [f.name for f in cls._meta.get_fields() 
                if f.is_relation and not f.many_to_many]

    @classmethod
    def get_all_with_related(cls):
        return cls.objects.select_related(*cls.get_related_fields())

class DocumentBase(models.Model):
    """
    Classe de base abstraite pour tous les documents
    """
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    reference = models.CharField(max_length=50, unique=True, editable=False)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=10,
        choices=BaseState.choices,
        default=BaseState.BROUILLON
    )
    doc_type = models.CharField(max_length=3)
    sequence_number = models.IntegerField()
    date_validation = models.DateTimeField(null=True, blank=True)

    objects = DocumentManager()

    class Meta:
        abstract = True

    @property
    def is_editable(self):
        return self.statut == BaseState.BROUILLON

    def generate_reference(self, **kwargs):
        """
        Génère une référence unique pour le document
        """
        if not self.sequence_number:
            self.sequence_number = self.__class__.objects.get_next_sequence(
                self.entity,
                self.doc_type,
                now().year,
                now().month
            )
        
        reference_parts = {
            'entity': self.entity.code,
            'doc_type': self.doc_type,
            'year': now().year,
            'month': now().month,
            'seq': self.sequence_number,
            **kwargs
        }
        
        return self.reference_pattern.format(**reference_parts)