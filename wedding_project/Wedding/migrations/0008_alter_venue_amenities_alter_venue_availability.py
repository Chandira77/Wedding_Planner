# Generated by Django 5.1.5 on 2025-02-09 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wedding', '0007_alter_venue_amenities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='amenities',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='availability',
            field=models.DateField(default=list),
        ),
    ]
