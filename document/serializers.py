# serializers.py
from rest_framework import serializers
from .models import (
    Entity, Client, Site, Category, Product, Offre, Proforma, 
    Affaire, Facture, Rapport, Formation, Participant, AttestationFormation
)

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'code', 'name']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'nom', 'email', 'telephone', 'adresse']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'nom', 'client', 'localisation', 'description']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'entity']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'category']

class OffreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offre
        fields = [
            'id', 'entity', 'reference', 'client', 'date_creation',
            'statut', 'doc_type', 'sequence_number', 'produit',
            'date_modification', 'date_validation', 'sites'
        ]
        read_only_fields = ['reference', 'sequence_number', 'date_creation']

class ProformaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proforma
        fields = [
            'id', 'entity', 'reference', 'client', 'date_creation',
            'statut', 'doc_type', 'sequence_number', 'offre'
        ]
        read_only_fields = ['reference', 'sequence_number', 'date_creation']

class AffaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affaire
        fields = [
            'id', 'entity', 'reference', 'client', 'date_creation',
            'statut', 'doc_type', 'sequence_number', 'offre',
            'date_debut', 'date_fin_prevue', 'statut_affaire'
        ]
        read_only_fields = ['reference', 'sequence_number', 'date_creation']

class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = [
            'id', 'entity', 'reference', 'client', 'date_creation',
            'statut', 'doc_type', 'sequence_number', 'affaire',
            'site', 'produit'
        ]
        read_only_fields = ['reference', 'sequence_number', 'date_creation']

class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = [
            'id', 'titre', 'client', 'affaire', 'rapport',
            'date_debut', 'date_fin', 'description'
        ]

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'nom', 'prenom', 'email', 'telephone', 'fonction', 'formation']

class AttestationFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttestationFormation
        fields = [
            'id', 'entity', 'reference', 'client', 'date_creation',
            'statut', 'doc_type', 'sequence_number', 'affaire',
            'formation', 'participant', 'details_formation'
        ]
        read_only_fields = ['reference', 'sequence_number', 'date_creation']
