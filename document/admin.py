from django.contrib import admin
from .models import Entity, Client, Site, Category, Product, Offre, Proforma, Facture, Rapport, Formation, Participant, \
    AttestationFormation, Affaire


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'telephone', 'adresse']
    search_fields = ['nom', 'email', 'telephone']


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'client', 'localisation']
    search_fields = ['nom', 'client__nom', 'localisation']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'entity']
    search_fields = ['code', 'name', 'entity__name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category']
    search_fields = ['code', 'name', 'category__name']



@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'entity', 'date_creation', 'statut']
    search_fields = ['reference', 'client__nom', 'produit__name']
    list_filter = ['statut', 'entity']

@admin.register(Affaire)
class AffaireAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'entity', 'date_creation', 'statut']
    search_fields = ['reference', 'client__nom']
    list_filter = ['statut', 'entity']

@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'entity', 'date_creation', 'statut']
    search_fields = ['reference', 'client__nom']
    list_filter = ['statut', 'entity']


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'entity', 'date_creation', 'statut']
    search_fields = ['reference', 'client__nom']
    list_filter = ['statut', 'entity']


@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'entity', 'date_creation', 'statut']
    search_fields = ['reference', 'client__nom']
    list_filter = ['statut', 'entity']


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'client', 'date_debut', 'date_fin', 'description']
    search_fields = ['titre', 'client__nom']
    list_filter = ['client']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'telephone', 'fonction', 'formation']
    search_fields = ['nom', 'prenom', 'email', 'fonction', 'formation__titre']
    list_filter = ['formation']


@admin.register(AttestationFormation)
class AttestationFormationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'entity', 'participant', 'formation', 'date_creation']
    search_fields = ['reference', 'client__nom', 'participant__nom', 'formation__titre']
    list_filter = ['entity', 'client', 'formation']


# Personnalisation de l'interface d'administration
admin.site.site_header = "Gestion des Documents"
admin.site.site_title = "Administration des Documents"
admin.site.index_title = "Tableau de bord"