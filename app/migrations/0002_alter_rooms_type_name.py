# Generated by Django 5.1.3 on 2024-11-27 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rooms',
            name='type_name',
            field=models.TextField(choices=[('Эконом', 'Эконом'), ('Люкс', 'Люкс'), ('Президентский', 'Президентский')], max_length=32),
        ),
    ]
