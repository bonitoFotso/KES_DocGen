from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'entities', EntityViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'sites', SiteViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'offres', OffreViewSet)
router.register(r'proformas', ProformaViewSet)
router.register(r'affaires', AffaireViewSet)
router.register(r'factures', FactureViewSet)
router.register(r'formations', FormationViewSet)
router.register(r'participants', ParticipantViewSet)
router.register(r'attestations', AttestationFormationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]