# Generated by Django 5.0.2 on 2024-03-06 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskapp', '0004_child_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='child',
            name='color',
        ),
    ]
