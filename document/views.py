from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import HasDocumentPermission, IsOwnerOrReadOnly
from .serializers import *


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class EntityViewSet(BaseViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    filterset_fields = ['code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']


class ClientViewSet(BaseViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filterset_fields = ['nom']
    search_fields = ['nom', 'email', 'telephone']
    ordering_fields = ['nom', 'created_at']

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        client = self.get_object()
        offres = Offre.objects.filter(client=client)
        serializer = OffreSerializer(offres, many=True)
        return Response(serializer.data)


class SiteViewSet(BaseViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    filterset_fields = ['client', 'nom']
    search_fields = ['nom', 'localisation']
    ordering_fields = ['nom', 'client__nom']


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['entity', 'code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']


class ProductViewSet(BaseViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'code']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']


class DocumentViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasDocumentPermission]

    def get_queryset(self):
        return self.queryset.prefetch_related('attachments').select_related(
            'client', 'entity', 'created_by', 'updated_by'
        )


class OffreViewSet(DocumentViewSet):
    queryset = Offre.objects.all()
    serializer_class = OffreSerializer
    filterset_fields = ['client', 'entity', 'statut']
    search_fields = ['reference', 'client__nom']
    ordering_fields = ['date_creation', 'date_modification']

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        offre = self.get_object()
        try:
            offre.statut = DocumentStatus.VALIDATED
            offre.save()
            return Response({'status': 'offre validée'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProformaViewSet(DocumentViewSet):
    queryset = Proforma.objects.all()
    serializer_class = ProformaSerializer
    filterset_fields = ['client', 'entity', 'statut']
    search_fields = ['reference', 'client__nom']
    ordering_fields = ['date_creation']


class AffaireViewSet(DocumentViewSet):
    queryset = Affaire.objects.all()
    serializer_class = AffaireSerializer
    filterset_fields = ['client', 'entity', 'statut', 'statut_affaire']
    search_fields = ['reference', 'client__nom']
    ordering_fields = ['date_debut', 'date_fin_prevue']

    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        affaire = self.get_object()
        affaire.statut_affaire = Affaire.AffaireStatus.TERMINEE
        affaire.save()
        return Response({'status': 'affaire terminée'})


class FactureViewSet(DocumentViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    filterset_fields = ['client', 'entity', 'statut']
    search_fields = ['reference', 'client__nom']
    ordering_fields = ['date_creation', 'montant_ttc']


class FormationViewSet(BaseViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    filterset_fields = ['client', 'proforma']
    search_fields = ['titre', 'client__nom']
    ordering_fields = ['date_debut', 'date_fin']

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        formation = self.get_object()
        participants = formation.participants.all()
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)


class ParticipantViewSet(BaseViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    filterset_fields = ['formation']
    search_fields = ['nom', 'prenom', 'email']
    ordering_fields = ['nom', 'prenom']


class AttestationFormationViewSet(DocumentViewSet):
    queryset = AttestationFormation.objects.all()
    serializer_class = AttestationFormationSerializer
    filterset_fields = ['formation', 'participant', 'statut']
    search_fields = ['reference', 'participant__nom']
    ordering_fields = ['date_creation']