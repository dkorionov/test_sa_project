# Generated by Django 5.0.7 on 2024-07-13 20:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['id'], 'verbose_name': 'Task', 'verbose_name_plural': 'Tasks'},
        ),
    ]
