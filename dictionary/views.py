from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Hint, Language, Translation, Word
from .forms import LanguageForm, WordForm, HintForm, TranslationForm


PAGINATOR_PER_PAGE = 20
RECENT_WORD_COUNT = 20


@login_required
def index(request):
    """
    URL: /dictionary/
    Renders a template with recent words and languages added.
    """

    recent_words = Word.objects.filter(user=request.user).order_by('-date_added')[:RECENT_WORD_COUNT]
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
    paginator = Paginator(all_words, PAGINATOR_PER_PAGE)
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
    paginator = Paginator(all_languages, PAGINATOR_PER_PAGE)
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
            'word_form': word_form,
            'hint_form': hint_form,
            'translation_form': translation_form,
        }
    )


@login_required
def add_language(request):
    """
    URL: /dictionary/languages/add
    Renders a form that creates a new language.
    """

    if request.method == 'POST':
        language_form = LanguageForm(request.POST)

        if language_form.is_valid():

            user = request.user

            # Creating a Language instance
            language_form.instance.user = user
            language_form.save()

            return HttpResponseRedirect(reverse('dictionary:languages_list'))

    else:
        language_form = LanguageForm()

    return render(
        request,
        'dictionary/add_language.html',
        {
            'language_form': language_form,
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
            'word_form': word_form,
            'hint_form': hint_form,
            'translation_form': translation_form,
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
        language_form = LanguageForm(request.POST, instance=language)

        if language_form.is_valid():

            # Creating a Language instance
            language_form.save()
            return HttpResponseRedirect(reverse('dictionary:language_detail', args=[language.pk]))

    else:
        language_form = LanguageForm(instance=language)

    return render(
        request,
        'dictionary/add_language.html',
        {
            'language_form': language_form,
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
