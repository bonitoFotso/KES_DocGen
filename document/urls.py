from django.urls import path
from .views import (
    AffaireListCreateView,
    ClientListCreateView,
    OffreListCreateView, OffreRetrieveUpdateDeleteView,
    ProformaListCreateView, ProformaRetrieveUpdateDeleteView,
    FactureListCreateView, FactureRetrieveUpdateDeleteView,
    RapportListCreateView, RapportRetrieveUpdateDeleteView, SiteListCreateView, CategoryListCreateView,
    ProductListCreateView, EntityListCreateView, ParticipantListCreateView, FormationListCreateView
)



urlpatterns = [
    path('entities/', EntityListCreateView.as_view(), name='client-list-create'),

    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('sites/', SiteListCreateView.as_view(), name='site-list-create'),
    path('participants/', ParticipantListCreateView.as_view(), name='participant-list-create'),
    path('formations/', FormationListCreateView.as_view(), name='formation-list-create'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('affaires/', AffaireListCreateView.as_view(), name='affaire-list-create'),

    path('offres/', OffreListCreateView.as_view(), name='offre-list-create'),
    path('offres/<int:pk>/', OffreRetrieveUpdateDeleteView.as_view(), name='offre-detail'),
    path('proformas/', ProformaListCreateView.as_view(), name='proforma-list-create'),
    path('proformas/<int:pk>/', ProformaRetrieveUpdateDeleteView.as_view(), name='proforma-detail'),
    path('factures/', FactureListCreateView.as_view(), name='facture-list-create'),
    path('factures/<int:pk>/', FactureRetrieveUpdateDeleteView.as_view(), name='facture-detail'),
    path('rapports/', RapportListCreateView.as_view(), name='rapport-list-create'),
    path('rapports/<int:pk>/', RapportRetrieveUpdateDeleteView.as_view(), name='rapport-detail'),
]
