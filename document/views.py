from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Entity, Client, Site, Category, Product, Offre, Proforma, 
    Affaire, Facture, Rapport, Formation, Participant, AttestationFormation
)
from .serializers import (
    # Entity serializers
    EntityListSerializer, EntityDetailSerializer, EntityEditSerializer,
    # Client serializers
    ClientListSerializer, ClientDetailSerializer, ClientEditSerializer,
    # Site serializers
    SiteListSerializer, SiteDetailSerializer, SiteEditSerializer,
    # Category serializers
    CategoryListSerializer, CategoryDetailSerializer, CategoryEditSerializer,
    # Product serializers
    ProductListSerializer, ProductDetailSerializer, ProductEditSerializer,
    # Offre serializers
    OffreListSerializer, OffreDetailSerializer, OffreEditSerializer,
    # Proforma serializers
    ProformaListSerializer, ProformaDetailSerializer, ProformaEditSerializer,
    # Affaire serializers
    AffaireListSerializer, AffaireDetailSerializer, AffaireEditSerializer,
    # Facture serializers
    FactureListSerializer, FactureDetailSerializer, FactureEditSerializer,
    # Rapport serializers
    RapportListSerializer, RapportDetailSerializer, RapportEditSerializer,
    # Formation serializers
    FormationListSerializer, FormationDetailSerializer, FormationEditSerializer,
    # Participant serializers
    ParticipantListSerializer, ParticipantDetailSerializer, ParticipantEditSerializer,
    # AttestationFormation serializers
    AttestationFormationListSerializer, AttestationFormationDetailSerializer, AttestationFormationEditSerializer,
)

class BaseModelViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        elif self.action in ['create', 'update', 'partial_update']:
            return self.edit_serializer_class
        return self.detail_serializer_class

class EntityViewSet(BaseModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntityListSerializer
    detail_serializer_class = EntityDetailSerializer
    edit_serializer_class = EntityEditSerializer
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']

class ClientViewSet(BaseModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientListSerializer
    detail_serializer_class = ClientDetailSerializer
    edit_serializer_class = ClientEditSerializer
    filterset_fields = ['nom']
    search_fields = ['nom', 'email']
    ordering_fields = ['nom']

    @action(detail=True, methods=['get'])
    def sites(self, request, pk=None):
        client = self.get_object()
        sites = Site.objects.filter(client=client)
        serializer = SiteListSerializer(sites, many=True)
        return Response(serializer.data)
    
class SiteViewSet(BaseModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteListSerializer
    detail_serializer_class = SiteDetailSerializer
    edit_serializer_class = SiteEditSerializer

    filterset_fields = ['client', 'nom']
    search_fields = ['nom', 'localisation']
    ordering_fields = ['nom']

class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer
    detail_serializer_class = CategoryDetailSerializer
    edit_serializer_class = CategoryEditSerializer
    filterset_fields = ['code', 'entity']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']

class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    detail_serializer_class = ProductDetailSerializer
    edit_serializer_class = ProductEditSerializer
    filterset_fields = ['code', 'category']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']

class OffreViewSet(BaseModelViewSet):
    queryset = Offre.objects.all()
    serializer_class = OffreListSerializer
    detail_serializer_class = OffreDetailSerializer
    edit_serializer_class = OffreEditSerializer
    filterset_fields = ['client', 'entity', 'statut', 'doc_type']
    search_fields = ['reference']
    ordering_fields = ['date_creation', 'date_modification']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OffreEditSerializer
        elif self.action == 'list':
            return OffreListSerializer
        return OffreDetailSerializer

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        offre = self.get_object()
        if offre.statut != 'BROUILLON':
            return Response(
                {"detail": "Seule une offre en brouillon peut être validée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        offre.statut = 'VALIDE'
        offre.save()
        return Response({"detail": "Offre validée avec succès."})

class ProformaViewSet(BaseModelViewSet):
    queryset = Proforma.objects.all()
    serializer_class = ProformaListSerializer
    detail_serializer_class = ProformaDetailSerializer
    edit_serializer_class = ProformaEditSerializer
    filterset_fields = ['client', 'entity', 'statut', 'doc_type']
    search_fields = ['reference']
    ordering_fields = ['date_creation']

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        proforma = self.get_object()
        if proforma.statut != 'BROUILLON':
            return Response(
                {"detail": "Seul un proforma en brouillon peut être validé."},
                status=status.HTTP_400_BAD_REQUEST
            )
        proforma.statut = 'VALIDE'
        proforma.save()
        return Response({"detail": "Proforma validé avec succès."})
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        proforma = self.get_object()

        # Vérifier si le nouveau statut est fourni dans la requête
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {"detail": "Le nouveau statut doit être fourni."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si le nouveau statut est valide
        valid_statuses = ['BROUILLON', 'VALIDE', 'ENVOYE']  # Ajoutez ici tous les statuts valides
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Le statut doit être l'un des suivants : {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mettre à jour le statut
        proforma.statut = new_status
        proforma.save()
        print(f"Statut du proforma mis à jour avec succès vers '{new_status}'.")

        return Response({
            "detail": f"Statut du proforma mis à jour avec succès vers '{new_status}'."
        })

class AffaireViewSet(BaseModelViewSet):
    queryset = Affaire.objects.all()
    serializer_class = AffaireListSerializer
    detail_serializer_class = AffaireDetailSerializer
    edit_serializer_class = AffaireEditSerializer
    filterset_fields = ['client', 'entity', 'statut']
    search_fields = ['reference']
    ordering_fields = ['date_debut', 'date_fin_prevue']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        affaire = serializer.save()
        response_serializer = self.detail_serializer_class(affaire)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def rapports(self, request, pk=None):
        affaire = self.get_object()
        rapports = Rapport.objects.filter(affaire=affaire)
        serializer = RapportListSerializer(rapports, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def formations(self, request, pk=None):
        affaire = self.get_object()
        formations = Formation.objects.filter(affaire=affaire)
        serializer = FormationListSerializer(formations, many=True)
        return Response(serializer.data)

class FactureViewSet(BaseModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureListSerializer
    detail_serializer_class = FactureDetailSerializer
    edit_serializer_class = FactureEditSerializer
    filterset_fields = ['client', 'entity', 'statut']
    search_fields = ['reference']
    ordering_fields = ['date_creation']

class RapportViewSet(BaseModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportListSerializer
    detail_serializer_class = RapportDetailSerializer
    edit_serializer_class = RapportEditSerializer
    filterset_fields = ['affaire', 'site', 'produit', 'statut']
    search_fields = ['reference']
    ordering_fields = ['date_creation']

class FormationViewSet(BaseModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationListSerializer
    detail_serializer_class = FormationDetailSerializer
    edit_serializer_class = FormationEditSerializer
    filterset_fields = ['client', 'affaire']
    search_fields = ['titre']
    ordering_fields = ['date_debut', 'date_fin']

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        formation = self.get_object()
        participants = Participant.objects.filter(formation=formation)
        serializer = ParticipantListSerializer(participants, many=True)
        return Response(serializer.data)

class ParticipantViewSet(BaseModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantListSerializer
    detail_serializer_class = ParticipantDetailSerializer
    edit_serializer_class = ParticipantEditSerializer
    filterset_fields = ['formation']
    search_fields = ['nom', 'prenom', 'email']
    ordering_fields = ['nom', 'prenom']

class AttestationFormationViewSet(BaseModelViewSet):
    queryset = AttestationFormation.objects.all()
    serializer_class = AttestationFormationListSerializer
    detail_serializer_class = AttestationFormationDetailSerializer
    edit_serializer_class = AttestationFormationEditSerializer
    filterset_fields = ['affaire', 'formation', 'participant']
    search_fields = ['reference']
    ordering_fields = ['date_creation']