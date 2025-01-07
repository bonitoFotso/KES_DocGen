# Generated by Django 5.1.4 on 2025-01-06 16:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_affaire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proforma',
            name='offre',
        ),
        migrations.AddField(
            model_name='proforma',
            name='affaire',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='proforma', to='document.affaire'),
            preserve_default=False,
        ),
    ]
