from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Affaire, Offre, Proforma, Facture, Rapport, Client, Site, Category, Product, Entity, Formation, Participant
from .serializers import AffaireListSerializer, AffaireSerializer, OffreSerializer, ProformaSerializer, FactureSerializer, RapportSerializer, ClientSerializer, \
    SiteSerializer, CategorySerializer, ProductSerializer, EntitySerializer, OffreListSerializer, FormationSerializer, \
    ParticipantSerializer, SiteListSerializer, ProductListSerializer, RapportListSerializer


class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = []
class EntityListCreateView(generics.ListCreateAPIView):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = []

class FormationListCreateView(generics.ListCreateAPIView):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    permission_classes = []
class ParticipantListCreateView(generics.ListCreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = []
class SiteListCreateView(generics.ListCreateAPIView):
    queryset = Site.objects.all()

    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SiteSerializer
        return SiteListSerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategorySerializer
        return CategorySerializer

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductSerializer
        return ProductListSerializer





class OffreListCreateView(generics.ListCreateAPIView):
    queryset = Offre.objects.all()

    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OffreSerializer
        return OffreListSerializer

class AffaireListCreateView(generics.ListCreateAPIView):
    queryset = Affaire.objects.all()

    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AffaireSerializer
        return AffaireListSerializer

class OffreRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offre.objects.all()
    serializer_class = OffreSerializer
    permission_classes = []


class ProformaListCreateView(generics.ListCreateAPIView):
    queryset = Proforma.objects.all()
    serializer_class = ProformaSerializer
    permission_classes = []


class ProformaRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proforma.objects.all()
    serializer_class = ProformaSerializer
    permission_classes = []


class FactureListCreateView(generics.ListCreateAPIView):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    permission_classes = []


class FactureRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    permission_classes = []


class RapportListCreateView(generics.ListCreateAPIView):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RapportSerializer
        return RapportListSerializer


class RapportRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    permission_classes = []
