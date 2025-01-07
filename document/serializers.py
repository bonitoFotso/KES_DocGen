from rest_framework import serializers
from .models import Offre, Proforma, Facture, Rapport, Client, Site, Product, Category, Entity, Participant, Formation, \
    Affaire


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = '__all__'

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OffreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offre
        fields = '__all__'


class AffaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affaire
        fields = '__all__'




class ProformaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proforma
        fields = '__all__'


class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'


class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = '__all__'

class OffreListSerializer(serializers.ModelSerializer):
    entity = EntitySerializer()
    client = ClientSerializer()
    category = CategorySerializer()
    produit = ProductSerializer()
    class Meta:
        model = Offre
        fields = '__all__'

class SiteListSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Site
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = '__all__'

class RapportListSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    class Meta:
        model = Rapport
        fields = '__all__'