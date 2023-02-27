# Generated by Django 4.1.7 on 2023-02-27 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_hint_user_language_user_translation_user_word_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='words', to='dictionary.language'),
        ),
    ]