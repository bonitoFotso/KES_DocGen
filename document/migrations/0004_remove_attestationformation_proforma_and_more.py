# Generated by Django 5.1.4 on 2025-01-07 12:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0003_remove_proforma_offre_proforma_affaire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attestationformation',
            name='proforma',
        ),
        migrations.RemoveField(
            model_name='facture',
            name='proforma',
        ),
        migrations.RemoveField(
            model_name='offre',
            name='category',
        ),
        migrations.RemoveField(
            model_name='proforma',
            name='affaire',
        ),
        migrations.RemoveField(
            model_name='rapport',
            name='proforma',
        ),
        migrations.AddField(
            model_name='attestationformation',
            name='affaire',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='attestations', to='document.affaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='facture',
            name='affaire',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='facture', to='document.affaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proforma',
            name='offre',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='proforma', to='document.offre'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rapport',
            name='affaire',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rapport', to='document.affaire'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='offre',
            name='produit',
        ),
        migrations.AddField(
            model_name='offre',
            name='produit',
            field=models.ManyToManyField(to='document.product'),
        ),
    ]
