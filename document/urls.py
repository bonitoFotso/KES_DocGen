from rest_framework.routers import DefaultRouter
from django.urls import path, include

from document.views import AffaireViewSet, AttestationFormationViewSet, ClientViewSet, EntityViewSet, FormationViewSet, OffreViewSet, ProformaViewSet, RapportViewSet, SiteViewSet

router = DefaultRouter()
router.register(r'entities', EntityViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'sites', SiteViewSet)
router.register(r'offres', OffreViewSet)
router.register(r'proformas', ProformaViewSet)
router.register(r'affaires', AffaireViewSet)
router.register(r'rapports', RapportViewSet)
router.register(r'formations', FormationViewSet)
router.register(r'attestations', AttestationFormationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]