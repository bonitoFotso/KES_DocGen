from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EntityViewSet,
    ClientViewSet,
    SiteViewSet,
    CategoryViewSet,
    ProductViewSet,
    OffreViewSet,
    ProformaViewSet,
    AffaireViewSet,
    FactureViewSet,
    RapportViewSet,
    FormationViewSet,
    ParticipantViewSet,
    AttestationFormationViewSet,
)

# Création du router
router = DefaultRouter()

# Enregistrement des routes
router.register(r'entities', EntityViewSet, basename='entity')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'sites', SiteViewSet, basename='site')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'offres', OffreViewSet, basename='offre')
router.register(r'proformas', ProformaViewSet, basename='proforma')
router.register(r'affaires', AffaireViewSet, basename='affaire')
router.register(r'factures', FactureViewSet, basename='facture')
router.register(r'rapports', RapportViewSet, basename='rapport')
router.register(r'formations', FormationViewSet, basename='formation')
router.register(r'participants', ParticipantViewSet, basename='participant')
router.register(r'attestations', AttestationFormationViewSet, basename='attestation')

app_name = 'api'

# Pattern des URLs
urlpatterns = [
    # Inclusion des URLs générées par le router
    path('', include(router.urls)),
    
    # URLs d'authentification de DRF
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Les URLs générées seront du type :
# /api/entities/
# /api/entities/{pk}/
# /api/clients/
# /api/clients/{pk}/
# /api/clients/{pk}/sites/
# /api/offres/
# /api/offres/{pk}/
# /api/offres/{pk}/valider/
# etc...