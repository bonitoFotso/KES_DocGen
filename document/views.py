# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

from document.permissions import IsEntityUser
from document.serializers import AffaireSerializer, AttestationFormationSerializer, ClientSerializer, EntitySerializer, FormationSerializer, OffreSerializer, ProformaSerializer, RapportSerializer, SiteSerializer
from .models import (
    Entity, Client, Site, Category, Product, Offre, Proforma, 
    Affaire, Facture, Rapport, Formation, Participant, AttestationFormation
)

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['code']

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['nom']

    def get_queryset(self):
        return Client.objects.filter(
            offre__entity__in=self.request.user.entities.all()
        ).distinct()

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['client']

    def get_queryset(self):
        return Site.objects.filter(
            client__offre__entity__in=self.request.user.entities.all()
        ).distinct()

class OffreViewSet(viewsets.ModelViewSet):
    queryset = Offre.objects.all()
    serializer_class = OffreSerializer
    permission_classes = [ IsEntityUser]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['client', 'statut', 'entity']

    def get_queryset(self):
        return Offre.objects.filter(
            entity__in=self.request.user.entities.all()
        )

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        offre = self.get_object()
        try:
            offre.validate()
            return Response({'status': 'offer validated'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ProformaViewSet(viewsets.ModelViewSet):
    queryset = Proforma.objects.all()
    serializer_class = ProformaSerializer
    permission_classes = [ IsEntityUser]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['client', 'statut', 'entity', 'offre']

    def get_queryset(self):
        return Proforma.objects.filter(
            entity__in=self.request.user.entities.all()
        )

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        proforma = self.get_object()
        try:
            proforma.validate()
            return Response({'status': 'proforma validated'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class AffaireViewSet(viewsets.ModelViewSet):
    queryset = Affaire.objects.all()
    serializer_class = AffaireSerializer
    permission_classes = [ IsEntityUser]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['client', 'statut', 'entity', 'offre', 'statut_affaire']

    def get_queryset(self):
        return Affaire.objects.filter(
            entity__in=self.request.user.entities.all()
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        affaire = self.get_object()
        try:
            affaire.complete_business()
            return Response({'status': 'business case completed'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class RapportViewSet(viewsets.ModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    permission_classes = [ IsEntityUser]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['client', 'statut', 'entity', 'affaire', 'site', 'produit']

    def get_queryset(self):
        return Rapport.objects.filter(
            entity__in=self.request.user.entities.all()
        )

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['client', 'affaire']

    def get_queryset(self):
        return Formation.objects.filter(
            affaire__entity__in=self.request.user.entities.all()
        )

class AttestationFormationViewSet(viewsets.ModelViewSet):
    queryset = AttestationFormation.objects.all()
    serializer_class = AttestationFormationSerializer
    permission_classes = [ IsEntityUser]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['client', 'statut', 'entity', 'affaire', 'formation', 'participant']

    def get_queryset(self):
        return AttestationFormation.objects.filter(
            entity__in=self.request.user.entities.all()
        )