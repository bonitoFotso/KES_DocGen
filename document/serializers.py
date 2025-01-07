from rest_framework import serializers
from .models import *


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class DocumentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAttachment
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class OffreSerializer(serializers.ModelSerializer):
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)
    produit = ProductSerializer(many=True, read_only=True)
    sites = SiteSerializer(many=True, read_only=True)

    class Meta:
        model = Offre
        fields = '__all__'
        read_only_fields = ('reference', 'created_by', 'updated_by', 'date_modification')


class ProformaSerializer(serializers.ModelSerializer):
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Proforma
        fields = '__all__'
        read_only_fields = ('reference', 'created_by', 'updated_by')


class AffaireSerializer(serializers.ModelSerializer):
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Affaire
        fields = '__all__'
        read_only_fields = ('reference', 'created_by', 'updated_by')


class FactureSerializer(serializers.ModelSerializer):
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Facture
        fields = '__all__'
        read_only_fields = ('reference', 'created_by', 'updated_by')


class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class AttestationFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttestationFormation
        fields = '__all__'
        read_only_fields = ('reference', 'created_by', 'updated_by')