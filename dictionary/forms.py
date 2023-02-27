from django.forms import ModelForm
from .models import Word, Hint, Translation, Language


class WordForm(ModelForm):
    def __init__(self, current_user, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['word_language'].queryset = Language.objects.filter(user=current_user)

    class Meta:
        model = Word
        fields = ['word', 'word_language', 'description']


class HintForm(ModelForm):
    class Meta:
        model = Hint
        fields = ['hint',]


class TranslationForm(ModelForm):
    def __init__(self, current_user, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['translation_language'].queryset = Language.objects.filter(user=current_user)

    class Meta:
        model = Translation
        fields = ['translation', 'translation_language']


class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = ['language_name',]
