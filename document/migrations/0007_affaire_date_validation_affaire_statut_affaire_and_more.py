# Generated by Django 5.1.4 on 2025-01-08 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_remove_formation_proforma_formation_affaire_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='affaire',
            name='date_validation',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='affaire',
            name='statut_affaire',
            field=models.CharField(choices=[('EN_COURS', 'En cours'), ('TERMINEE', 'Terminée'), ('ANNULEE', 'Annulée')], default='EN_COURS', max_length=20),
        ),
        migrations.AddField(
            model_name='attestationformation',
            name='date_validation',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='facture',
            name='date_validation',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='proforma',
            name='date_validation',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rapport',
            name='date_validation',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='affaire',
            name='reference',
            field=models.CharField(editable=False, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='affaire',
            name='sequence_number',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='affaire',
            name='statut',
            field=models.CharField(choices=[('BROUILLON', 'Brouillon'), ('ENVOYE', 'Envoyé'), ('VALIDE', 'Validé'), ('REFUSE', 'Refusé')], default='BROUILLON', max_length=10),
        ),
        migrations.AlterField(
            model_name='attestationformation',
            name='reference',
            field=models.CharField(editable=False, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='attestationformation',
            name='sequence_number',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='facture',
            name='reference',
            field=models.CharField(editable=False, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='facture',
            name='sequence_number',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='offre',
            name='reference',
            field=models.CharField(editable=False, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='offre',
            name='sequence_number',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='proforma',
            name='reference',
            field=models.CharField(editable=False, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='proforma',
            name='sequence_number',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='rapport',
            name='reference',
            field=models.CharField(editable=False, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='rapport',
            name='sequence_number',
            field=models.IntegerField(editable=False),
        ),
    ]