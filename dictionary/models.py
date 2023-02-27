from django.db import models
from django.contrib.auth.models import User


class Language(models.Model):
    """Model representing a language."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='languages')
    language_name = models.CharField(verbose_name="Language (eg. English, Russian)", max_length=300)
    date_added = models.DateTimeField(verbose_name="Date and time when the language is added", auto_now_add=True)

    def __str__(self):
        return f"{ self.language_name }"


class Word(models.Model):
    """
    Model representing a single word.
    """

    word = models.CharField(verbose_name="Word", max_length=300)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='words')
    word_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='words', verbose_name="Word's language")
    description = models.TextField(verbose_name="Word's description")
    date_added = models.DateTimeField(verbose_name="Date and time when the word is added", auto_now_add=True)

    def __str__(self):
        return f"{ self.word }"


class Hint(models.Model):
    """Model representing words' hints."""

    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='hints')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hints')
    hint = models.CharField(verbose_name="Word's hint", max_length=300)
    date_added = models.DateTimeField(verbose_name="Date and time when the hint is added", auto_now_add=True)

    def __str__(self):
        return f"{ self.hint }"


class Translation(models.Model):
    """Model representing word's translations."""

    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='translations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translations')
    translation_language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name="Translation's language")
    translation = models.CharField(verbose_name="Word's translation", max_length=300)
    date_added = models.DateTimeField(verbose_name="Date and time when the translation is added", auto_now_add=True)

    def __str__(self):
        return f"{ self.translation }"
