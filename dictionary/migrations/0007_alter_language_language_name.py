# Generated by Django 4.1.7 on 2023-03-12 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_alter_language_language_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='language_name',
            field=models.CharField(max_length=300, verbose_name='Language (eg. English, Russian)'),
        ),
    ]
