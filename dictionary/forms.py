from django.forms import CharField, ModelForm, Form, FileField
from django.core.validators import FileExtensionValidator

from dictionary.validators import FileSizeValidator

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
    def __init__(self, current_user, *args, **kargs):
        super().__init__(*args, **kargs)
        self.current_user = current_user

    class Meta:
        model = Language
        fields = ['language_name',]

    def clean(self):
        """Function that validates that the user cannot create a language that already exists"""

        cleaned_data = super().clean()
        language_name = cleaned_data.get("language_name")

        # Only do something if field is valid so far
        if language_name:
            try:
                Language.objects.get(user=self.current_user, language_name__iexact=language_name)
                self.add_error('language_name', "Language with that name already exists!")

            except Language.DoesNotExist:
                pass

        return cleaned_data


class DictionaryFileForm(Form):
    file = FileField(
        help_text='You must provide a valid .csv file that is no larger than 5MB',
        validators=[
            FileExtensionValidator(allowed_extensions=['csv']),
            FileSizeValidator(max_size=2_500_000),
        ],
    )


class SearchForm(Form):
    word = CharField(max_length=150)