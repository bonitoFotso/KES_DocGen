from rest_framework import serializers
from .models import (
    Entity, Client, Site, Category, Product, Offre, Proforma, 
    Affaire, Facture, Rapport, Formation, Participant, AttestationFormation
)

# Entity Serializers
class EntityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'code', 'name']

class EntityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'

# Client Serializers
class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'nom', 'email']

class ClientDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Client
        fields = '__all__'

# Site Serializers
class SiteListSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    clientId = serializers.IntegerField(source='client.id', read_only=True)
    
    class Meta:
        model = Site
        fields = ['id', 'nom', 'client_nom', 'localisation', 'clientId']

class SiteDetailSerializer(serializers.ModelSerializer):
    client = ClientListSerializer(read_only=True)
    class Meta:
        model = Site
        fields = '__all__'

class SiteEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'

# Category Serializers
class CategoryListSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.name', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'entity_name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Product Serializers
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    categoryId = serializers.IntegerField(source='category.id', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'category_name', 'categoryId']

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# Offre Serializers
class OffreListSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    
    class Meta:
        model = Offre
        fields = ['id', 'reference', 'client_nom', 'entity_code', 'statut', 'date_creation']

class OffreDetailSerializer(serializers.ModelSerializer):
    entity = EntityDetailSerializer(read_only=True)
    client = ClientDetailSerializer(read_only=True)
    sites = SiteListSerializer(many=True, read_only=True)
    produit = ProductListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Offre
        fields = '__all__'

class OffreEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offre
        fields = ['client', 'entity', 'statut', 'sites', 'produit','doc_type']

# Proforma Serializers
class ProformaListSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    offre_reference = serializers.CharField(source='offre.reference', read_only=True)
    
    class Meta:
        model = Proforma
        fields = ['id', 'reference', 'client_nom', 'offre_reference', 'statut', 'date_creation']

class ProformaDetailSerializer(serializers.ModelSerializer):
    offre = OffreListSerializer(read_only=True)
    entity = EntityDetailSerializer(read_only=True)
    client = ClientDetailSerializer(read_only=True)
    
    class Meta:
        model = Proforma
        fields = '__all__'

# Affaire Serializers
class AffaireListSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    offre_reference = serializers.CharField(source='offre.reference', read_only=True)
    
    class Meta:
        model = Affaire
        fields = ['id', 'reference', 'client_nom', 'offre_reference', 'statut', 'date_debut', 'date_fin_prevue']

class AffaireDetailSerializer(serializers.ModelSerializer):
    offre = OffreDetailSerializer(read_only=True)
    rapports = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    formations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Affaire
        fields = '__all__'

# Facture Serializers
class FactureListSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    affaire_reference = serializers.CharField(source='affaire.reference', read_only=True)
    
    class Meta:
        model = Facture
        fields = ['id', 'reference', 'client_nom', 'affaire_reference', 'statut', 'date_creation']

class FactureDetailSerializer(serializers.ModelSerializer):
    affaire = AffaireListSerializer(read_only=True)
    
    class Meta:
        model = Facture
        fields = '__all__'

# Rapport Serializers
class RapportListSerializer(serializers.ModelSerializer):
    affaire = AffaireListSerializer(read_only=True)
    site = SiteListSerializer(read_only=True)
    produit = ProductListSerializer(read_only=True)    
    class Meta:
        model = Rapport
        fields = ['id', 'reference', 'site', 'produit', 'statut', 'date_creation', 'affaire']

class RapportDetailSerializer(serializers.ModelSerializer):
    affaire = AffaireListSerializer(read_only=True)
    site = SiteDetailSerializer(read_only=True)
    produit = ProductDetailSerializer(read_only=True)
    
    class Meta:
        model = Rapport
        fields = '__all__'

# Formation Serializers
class FormationListSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    affaire_reference = serializers.CharField(source='affaire.reference', read_only=True)
    
    class Meta:
        model = Formation
        fields = ['id', 'titre', 'client_nom', 'affaire_reference', 'date_debut', 'date_fin']

class FormationDetailSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    attestations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Formation
        fields = '__all__'

# Participant Serializers
class ParticipantListSerializer(serializers.ModelSerializer):
    formation_titre = serializers.CharField(source='formation.titre', read_only=True)
    
    class Meta:
        model = Participant
        fields = ['id', 'nom', 'prenom', 'email', 'formation_titre']

class ParticipantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

# AttestationFormation Serializers
class AttestationFormationListSerializer(serializers.ModelSerializer):
    participant_nom = serializers.SerializerMethodField()
    formation_titre = serializers.CharField(source='formation.titre', read_only=True)
    
    class Meta:
        model = AttestationFormation
        fields = ['id', 'reference', 'participant_nom', 'formation_titre', 'date_creation']
    
    def get_participant_nom(self, obj):
        return f"{obj.participant.nom} {obj.participant.prenom}"

class AttestationFormationDetailSerializer(serializers.ModelSerializer):
    participant = ParticipantDetailSerializer(read_only=True)
    formation = FormationListSerializer(read_only=True)
    affaire = AffaireListSerializer(read_only=True)
    
    class Meta:
        model = AttestationFormation
        fields = '__all__'

# Entity Edit Serializer
class EntityEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'

# Client Edit Serializer
class ClientEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

# Category Edit Serializer
class CategoryEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Product Edit Serializer
class ProductEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# Proforma Edit Serializer
class ProformaEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proforma
        fields = ['offre', 'entity', 'client', 'statut']

# Affaire Edit Serializer
class AffaireEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affaire
        fields = ['offre', 'statut', 'date_debut', 'date_fin_prevue']

# Facture Edit Serializer
class FactureEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = ['affaire', 'client', 'statut', 'montant', 'date_echeance']

# Rapport Edit Serializer
class RapportEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = ['affaire', 'site', 'produit', 'statut',]

# Formation Edit Serializer
class FormationEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = ['affaire', 'client', 'titre', 'description', 'date_debut', 'date_fin']

# Participant Edit Serializer
class ParticipantEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

# AttestationFormation Edit Serializer
class AttestationFormationEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttestationFormation
        fields = ['participant', 'formation', 'affaire', 'contenu']