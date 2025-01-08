from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    Entity, Client, Site, Category, Product, Offre, Proforma, 
    Affaire, Facture, Rapport, Formation, Participant, AttestationFormation
)

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'get_offres_count', 'get_affaires_count')
    search_fields = ('code', 'name')
    ordering = ('code',)

    def get_offres_count(self, obj):
        return obj.offre_set.count()
    get_offres_count.short_description = 'Offres'

    def get_affaires_count(self, obj):
        return obj.affaire_set.count()
    get_affaires_count.short_description = 'Affaires'

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'get_sites_count', 'get_offres_count')
    search_fields = ('nom', 'email', 'telephone')
    list_filter = ('site__nom',)

    def get_sites_count(self, obj):
        return obj.site_set.count()
    get_sites_count.short_description = 'Sites'

    def get_offres_count(self, obj):
        return obj.offre_set.count()
    get_offres_count.short_description = 'Offres'

class SiteInline(admin.TabularInline):
    model = Site
    extra = 1

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'client', 'localisation')
    search_fields = ('nom', 'client__nom', 'localisation')
    list_filter = ('client',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'entity')
    search_fields = ('code', 'name')
    list_filter = ('entity',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category')
    search_fields = ('code', 'name')
    list_filter = ('category',)

class ProformaInline(admin.TabularInline):
    model = Proforma
    readonly_fields = ('reference',)
    extra = 0
    can_delete = False

@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'client', 'entity', 'statut', 
        'date_creation', 'get_proforma_link'
    )
    list_filter = ('statut', 'entity', 'date_creation')
    search_fields = ('reference', 'client__nom')
    readonly_fields = ('reference', 'sequence_number')
    filter_horizontal = ('produit', 'sites')
    inlines = [ProformaInline]
    date_hierarchy = 'date_creation'

    def get_proforma_link(self, obj):
        if hasattr(obj, 'proforma'):
            url = reverse('admin:app_proforma_change', args=[obj.proforma.id])
            return format_html('<a href="{}">{}</a>', url, obj.proforma.reference)
        return '-'
    get_proforma_link.short_description = 'Proforma'

class AffaireInline(admin.TabularInline):
    model = Affaire
    readonly_fields = ('reference',)
    extra = 0
    can_delete = False

@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'client', 'entity', 'statut', 
        'date_creation', 'get_affaire_link'
    )
    list_filter = ('statut', 'entity', 'date_creation')
    search_fields = ('reference', 'client__nom')
    readonly_fields = ('reference', 'sequence_number')
    #inlines = [AffaireInline]
    date_hierarchy = 'date_creation'

    def get_affaire_link(self, obj):
        if hasattr(obj, 'affaire'):
            url = reverse('admin:app_affaire_change', args=[obj.affaire.id])
            return format_html('<a href="{}">{}</a>', url, obj.affaire.reference)
        return '-'
    get_affaire_link.short_description = 'Affaire'

class RapportInline(admin.TabularInline):
    model = Rapport
    readonly_fields = ('reference',)
    extra = 1

class FormationInline(admin.StackedInline):
    model = Formation
    extra = 1

@admin.register(Affaire)
class AffaireAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'client', 'entity', 'statut', 
        'statut_affaire', 'date_debut', 'date_fin_prevue'
    )
    list_filter = ('statut', 'entity', 'statut_affaire', 'date_debut')
    search_fields = ('reference', 'client__nom')
    readonly_fields = ('reference', 'sequence_number')
    inlines = [RapportInline, FormationInline]
    date_hierarchy = 'date_debut'

    fieldsets = (
        ('Informations générales', {
            'fields': ('entity', 'client', 'offre')
        }),
        ('Statut', {
            'fields': ('statut', 'statut_affaire')
        }),
        ('Dates', {
            'fields': ('date_debut', 'date_fin_prevue')
        }),
        ('Références', {
            'fields': ('reference', 'sequence_number'),
            'classes': ('collapse',)
        }),
    )

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'client', 'affaire', 'date_debut', 'date_fin')
    list_filter = ('client', 'date_debut')
    search_fields = ('titre', 'client__nom')
    inlines = [ParticipantInline]
    date_hierarchy = 'date_debut'

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'fonction', 'formation')
    list_filter = ('formation', 'fonction')
    search_fields = ('nom', 'prenom', 'email')

@admin.register(AttestationFormation)
class AttestationFormationAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'client', 'entity', 'participant', 
        'formation', 'date_creation'
    )
    list_filter = ('entity', 'formation', 'date_creation')
    search_fields = ('reference', 'client__nom', 'participant__nom')
    readonly_fields = ('reference', 'sequence_number')
    date_hierarchy = 'date_creation'

    fieldsets = (
        ('Informations générales', {
            'fields': ('entity', 'client', 'affaire', 'formation', 'participant')
        }),
        ('Détails', {
            'fields': ('details_formation',)
        }),
        ('Références', {
            'fields': ('reference', 'sequence_number'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'entity', 'statut', 'date_creation')
    list_filter = ('statut', 'entity', 'date_creation')
    search_fields = ('reference', 'client__nom')
    readonly_fields = ('reference', 'sequence_number')
    date_hierarchy = 'date_creation'