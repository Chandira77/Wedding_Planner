# Generated by Django 5.1.5 on 2025-02-25 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Wedding', '0019_remove_guest_rsvp_status_guest_assigned_side_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guest',
            name='event',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
    ]
