# Generated by Django 5.1.5 on 2025-02-09 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='business_category',
            field=models.CharField(blank=True, choices=[('decoration', 'Decoration'), ('catering', 'Catering'), ('photography', 'Photography'), ('videography', 'Videography')], max_length=50, null=True),
        ),
    ]
