# Generated by Django 4.1.7 on 2023-03-12 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0005_rename_language_translation_translation_language_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='language_name',
            field=models.CharField(max_length=300, unique=True, verbose_name='Language (eg. English, Russian)'),
        ),
    ]
