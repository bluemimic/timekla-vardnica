from django.core.exceptions import PermissionDenied, NON_FIELD_ERRORS
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db import transaction

from django.conf import settings as stg

from app.utils import bootstrapify_form

from .models import Hint, Language, Translation, Word
from .forms import DictionaryFileForm, LanguageForm, WordForm, HintForm, TranslationForm

import io
import pandas as pd


@login_required
def index(request):
    """
    URL: /dictionary/
    Renders a template with recent words and languages added.
    """

    recent_words = Word.objects.filter(user=request.user).order_by('-date_added')[:stg.RECENT_WORD_COUNT]
    users_languages = Language.objects.filter(user=request.user).order_by('-date_added')

    context = {
        'recent_words': recent_words,
        'languages': users_languages,
    }

    return render(request, "dictionary/index.html", context)


@login_required
def words_list(request):
    """
    URL: /dictionary/words
    Renders a template with all words added, sorted by creation time in descending order.
    Pagination is used to split words to equal groups.
    """

    all_words = Word.objects.filter(user=request.user).order_by('-date_added')
    paginator = Paginator(all_words, stg.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')

    # get_page returns a valid page even if a page_number value is not valid
    page_obj = paginator.get_page(page_number)

    context = {'words': page_obj}

    return render(request, 'dictionary/words_list.html', context)


@login_required
def languages_list(request):
    """
    URL: /dictionary/languages
    Renders a template with all languages added, sorted by creation time in descending order.
    Pagination is used to split words to equal groups.
    """

    all_languages = Language.objects.filter(user=request.user).order_by('-date_added')
    paginator = Paginator(all_languages, stg.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')

    # get_page returns a valid page even if a page_number value is not valid
    page_obj = paginator.get_page(page_number)

    context = {'languages': page_obj}

    return render(request, 'dictionary/languages_list.html', context)


@login_required
def word_detail(request, word_id: int):
    """
    URL: /dictionary/words/<int: word_id>
    Renders a template with the information about the word provided if the word exists, otherwise throws 404 error.
    """

    word = get_object_or_404(Word, pk=word_id)

    if word.user != request.user:
        raise PermissionDenied()

    translations = list(Translation.objects.filter(word=word, user=word.user))
    hints = list(Hint.objects.filter(word=word, user=word.user))

    context = {
        'word': word,
        'translations': translations,
        'hints': hints
    }

    return render(request, 'dictionary/word_detail.html', context)


@login_required
def language_detail(request, language_id: int):
    """
    URL: /dictionary/languages/<int: language_id>
    Renders a template with the information about the language provided if the word exists, otherwise throws 404 error.
    """

    language = get_object_or_404(Language, pk=language_id)

    if language.user != request.user:
        raise PermissionDenied()

    context = {
        'language': language,
    }

    return render(request, 'dictionary/language_detail.html', context)


@login_required
def add_word(request):
    """
    URL: /dictionary/words/add
    Renders a form that creates a new word, alongsige with a hint and a traslation related.
    """

    if request.method == 'POST':
        word_form = WordForm(request.user, request.POST)
        hint_form = HintForm(request.POST)
        translation_form = TranslationForm(request.user, request.POST)

        if all([word_form.is_valid(), hint_form.is_valid(), translation_form.is_valid()]):

            # Check if the translation's language and the word's one are different
            word_language = word_form.cleaned_data.get('word_language')
            translation_language = translation_form.cleaned_data.get('translation_language')

            if word_language == translation_language:
                word_form.add_error(None, "Word's language and translation's language cannot be the same!")

            if not word_form.has_error(NON_FIELD_ERRORS):
                user = request.user

                # Creating a Word instance
                word_form.instance.user = user
                new_word = word_form.save()

                # Creating a Hint instance
                hint_form.instance.word = new_word
                hint_form.instance.user = user
                hint_form.save()

                # Creating a Translation instance
                translation_form.instance.word = new_word
                translation_form.instance.user = user
                translation_form.save()

                return HttpResponseRedirect(reverse('dictionary:words_list'))

    else:
        word_form = WordForm(current_user=request.user)
        hint_form = HintForm()
        translation_form = TranslationForm(current_user=request.user)


    return render(
        request,
        'dictionary/add_word.html',
        {
            'word_form': bootstrapify_form(word_form),
            'hint_form': bootstrapify_form(hint_form),
            'translation_form': bootstrapify_form(translation_form),
        }
    )


@transaction.atomic
@login_required
def add_words_from_file(request):
    """
    URL: /dictionary/words/add/from_file
    Handles .csv file upload with words and tries to save those in the database.
    """

    if request.method == 'POST':
        dictionary_file_form = DictionaryFileForm(request.POST, request.FILES)

        if dictionary_file_form.is_valid():

            user = request.user
            file = dictionary_file_form.cleaned_data['file'].read()
            csv = io.BytesIO(file)

            # Different schemas could be added in the future
            allowed_column_schemas = [
                ['Word', 'WordLanguage', 'Description', 'Hint', 'Translation', 'TranslationLanguage'],
            ]

            df = pd.read_csv(csv)
            schema = list(df.columns)

            # Validating data
            if df.isnull().values.any():
                dictionary_file_form.add_error('file', f"File does not contain enough data to proceed!")

            if schema not in allowed_column_schemas:
                dictionary_file_form.add_error('file', f"File schema [{ ', '.join(schema) }] is invalid! See help for more infornation.")

            if not dictionary_file_form.has_error('file'):

                # Iterating over elements in .csv file
                for _, row in df.iterrows():
                    word                    = row['Word'].capitalize()
                    word_language           = row['WordLanguage'].capitalize()
                    description             = row['Description'].capitalize()
                    hint                    = row['Hint'].capitalize()
                    translation             = row['Translation'].capitalize()
                    translation_language    = row['TranslationLanguage'].capitalize()

                    all_languages = [lang.language_name.lower() for lang in Language.objects.filter(user=user)]

                    # Adding languages if needed
                    try:
                        if (word_language.lower() not in all_languages):
                            new_language = Language(user=user, language_name=word_language)

                            new_language.full_clean()
                            new_language.save()

                        if (translation_language.lower() not in all_languages):
                            new_language = Language(user=user, language_name=translation_language)

                            new_language.full_clean()
                            new_language.save()

                    except ValidationError:
                        dictionary_file_form.add_error('file', "File data is invalid1!")
                        transaction.set_rollback(True)
                        break

                    word_language = Language.objects.get(user=user, language_name=word_language)
                    translation_language = Language.objects.get(user=user, language_name=translation_language)

                    # Adding new instances
                    new_word = Word(word=word, user=user, word_language=word_language, description=description)
                    new_hint = Hint(word=new_word, user=user, hint=hint)
                    new_translation = Translation(word=new_word, user=user, translation_language=translation_language, translation=translation)

                    # Validating them
                    try:
                        new_word.full_clean()
                        new_word.save()

                        for new_instance in [new_hint, new_translation]:
                            new_instance.word = new_word
                            new_instance.full_clean()
                            new_instance.save()

                    except ValidationError:
                        dictionary_file_form.add_error('file', "File data is invalid2!")
                        transaction.set_rollback(True)
                        break

            if not dictionary_file_form.has_error('file'):
                return HttpResponseRedirect(reverse('dictionary:words_list'))

    else:
        dictionary_file_form = DictionaryFileForm()


    return render(
        request,
        'dictionary/add_words_from_file.html',
        {
            'dictionary_file_form': bootstrapify_form(dictionary_file_form),
        }
    )


@login_required
def add_language(request):
    """
    URL: /dictionary/languages/add
    Renders a form that creates a new language.
    """

    if request.method == 'POST':
        language_form = LanguageForm(request.user, request.POST)

        if language_form.is_valid():

            user = request.user

            # Creating a Language instance
            language_form.instance.user = user
            language_form.save()

            return HttpResponseRedirect(reverse('dictionary:languages_list'))

    else:
        language_form = LanguageForm(request.user)

    return render(
        request,
        'dictionary/add_language.html',
        {
            'language_form': bootstrapify_form(language_form),
        }
    )


@login_required
def edit_word(request, word_id: int):
    """
    URL: /dictionary/words/edit/<int: language_id>
    Renders a form that allow user to edit a word, alongside with the corresponding
    hints and translations.
    """

    word = get_object_or_404(Word, pk=word_id)

    if word.user != request.user:
        raise PermissionDenied()

    hint = Hint.objects.get(word=word, user=word.user)
    translation = Translation.objects.get(word=word, user=word.user)

    if request.method == 'POST':
        word_form = WordForm(request.user, request.POST, instance=word)
        hint_form = HintForm(request.POST, instance=hint)
        translation_form = TranslationForm(request.user, request.POST, instance=translation)

        if all([word_form.is_valid(), hint_form.is_valid(), translation_form.is_valid()]):

            # Updating instances
            word_form.save()
            hint_form.save()
            translation_form.save()

            return HttpResponseRedirect(reverse('dictionary:word_detail', args=[word.pk]))

    else:
        word_form = WordForm(request.user, instance=word)
        hint_form = HintForm(instance=hint)
        translation_form = TranslationForm(request.user, instance=translation)

    return render(
        request,
        'dictionary/add_word.html',
        {
            'word_form': bootstrapify_form(word_form),
            'hint_form': bootstrapify_form(hint_form),
            'translation_form': bootstrapify_form(translation_form),
            'update': True,
        }
    )


@login_required
def edit_language(request, language_id: int):
    """
    URL: /dictionary/languages/edit/<int: language_id>
    Renders a form that allow user to edit a language.
    """

    language = get_object_or_404(Language, pk=language_id)

    if language.user != request.user:
        raise PermissionDenied()

    if request.method == 'POST':
        language_form = LanguageForm(request.user, request.POST, instance=language)

        if language_form.is_valid():

            # Creating a Language instance
            language_form.save()
            return HttpResponseRedirect(reverse('dictionary:language_detail', args=[language.pk]))

    else:
        language_form = LanguageForm(current_user=request.user, instance=language)

    return render(
        request,
        'dictionary/add_language.html',
        {
            'language_form': bootstrapify_form(language_form),
            'update': True,
        }
    )


@login_required
def delete_word(request, word_id: int):
    """
    URL: /dictionary/languages/delete/<int: language_id>
    Deletes a word and other related instances, eg. Hints, Translations.
    """

    word = get_object_or_404(Word, pk=word_id)

    if word.user != request.user:
        raise PermissionDenied()

    word.delete()

    return HttpResponseRedirect(reverse('dictionary:words_list'))


@login_required
def delete_language(request, language_id: int):
    """
    URL: /dictionary/languages/delete/<int: language_id>
    Deletes a language.
    """

    language = get_object_or_404(Language, pk=language_id)

    if language.user != request.user:
        raise PermissionDenied()

    language.delete()

    return HttpResponseRedirect(reverse('dictionary:languages_list'))
