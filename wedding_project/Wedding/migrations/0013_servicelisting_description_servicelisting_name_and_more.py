# Generated by Django 5.1.5 on 2025-02-16 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wedding', '0012_cateringservice'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicelisting',
            name='description',
            field=models.TextField(default='No description available'),
        ),
        migrations.AddField(
            model_name='servicelisting',
            name='name',
            field=models.CharField(default='Unnamed Service', max_length=255),
        ),
        migrations.DeleteModel(
            name='CateringService',
        ),
    ]
