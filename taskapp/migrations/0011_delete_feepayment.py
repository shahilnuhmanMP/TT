# Generated by Django 5.0.2 on 2024-05-28 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskapp', '0010_alter_event_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FeePayment',
        ),
    ]
