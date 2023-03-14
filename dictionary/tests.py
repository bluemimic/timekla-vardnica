from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.paginator import Paginator, Page
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from django.conf import settings as stg

from dictionary.models import Hint, Language, Translation, Word


@override_settings(RECENT_WORD_COUNT=3)
class IndexTests(TestCase):
    """
    Tests `index` view
    URL: /dictionary/
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

        for i in range(stg.RECENT_WORD_COUNT + 1):
            Word.objects.create(word=f"Word{ i } U{ cls.user1 }",
                                user=cls.user1,
                                word_language=cls.language1,
                                description=f'Word\'s{ i } description'
                                )

            Word.objects.create(word=f"Word{ i } U{ cls.user2 }",
                                user=cls.user2,
                                word_language=cls.language2,
                                description=f'Word\'s{ i } description'
                                )

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:index'))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:index") }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:index'))

        self.assertEqual(response.status_code, 200)

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:index'))

        self.assertTemplateUsed(response, 'dictionary/index.html')

    def test_context(self):
        """Test if context contains correct values"""

        response = self.client.get(reverse('dictionary:index'))

        recent_words = Word.objects.filter(user=self.user1).order_by('-date_added')[:stg.RECENT_WORD_COUNT]
        users_languages = Language.objects.filter(user=self.user1).order_by('-date_added')

        response_recent_words = response.context['recent_words']
        response_users_languages = response.context['languages']

        self.assertQuerysetEqual(response_recent_words, recent_words)
        self.assertQuerysetEqual(response_users_languages, users_languages)


@override_settings(PAGINATOR_PER_PAGE=3)
class WordsListTests(TestCase):
    """
    Tests `words_list` view
    URL: /dictionary/words/
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

        for i in range(stg.PAGINATOR_PER_PAGE + 1):
            Word.objects.create(word=f"Word{ i } U{ cls.user1 }",
                                user=cls.user1,
                                word_language=cls.language1,
                                description=f'Word\'s{ i } description'
                                )

            Word.objects.create(word=f"Word{ i } U{ cls.user2 }",
                                user=cls.user2,
                                word_language=cls.language2,
                                description=f'Word\'s{ i } description'
                                )

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:words_list'))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:words_list") }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:words_list'))

        self.assertEqual(response.status_code, 200)

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:words_list'))

        self.assertTemplateUsed(response, 'dictionary/words_list.html')

    def test_context(self):
        """Test if context contains correct values"""

        response = self.client.get(reverse('dictionary:words_list'))

        all_words = Word.objects.filter(user=self.user1).order_by('-date_added')
        paginator = Paginator(all_words, stg.PAGINATOR_PER_PAGE)
        page_obj = paginator.get_page(1)

        response_words_page_object = response.context['words']

        # Test if `words` is a page object
        self.assertIsInstance(response_words_page_object, Page)
        self.assertQuerysetEqual(response_words_page_object.object_list, page_obj.object_list)
        self.assertTrue(response_words_page_object.has_other_pages())
        self.assertEqual(response_words_page_object.next_page_number(), 2)

        self.assertQuerysetEqual(all_words[:3], response_words_page_object.object_list)


@override_settings(PAGINATOR_PER_PAGE=1)
class LanguagesListTests(TestCase):
    """
    Tests `languages_list` view
    URL: /dictionary/languages/
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

        for i in range(stg.PAGINATOR_PER_PAGE + 1):
            Word.objects.create(word=f"Word{ i } U{ cls.user1 }",
                                user=cls.user1,
                                word_language=cls.language1,
                                description=f'Word\'s{ i } description'
                                )

            Word.objects.create(word=f"Word{ i } U{ cls.user2 }",
                                user=cls.user2,
                                word_language=cls.language2,
                                description=f'Word\'s{ i } description'
                                )

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:languages_list'))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:languages_list") }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:languages_list'))

        self.assertEqual(response.status_code, 200)

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:languages_list'))

        self.assertTemplateUsed(response, 'dictionary/languages_list.html')

    def test_context(self):
        """Test if context contains correct values"""

        response = self.client.get(reverse('dictionary:languages_list'))

        all_languages = Language.objects.filter(user=self.user1).order_by('-date_added')
        paginator = Paginator(all_languages, stg.PAGINATOR_PER_PAGE)
        page_obj = paginator.get_page(1)

        response_languages_page_object = response.context['languages']

        # Test if `words` is a page object
        self.assertIsInstance(response_languages_page_object, Page)
        self.assertQuerysetEqual(response_languages_page_object.object_list, page_obj.object_list)
        self.assertTrue(response_languages_page_object.has_other_pages())
        self.assertEqual(response_languages_page_object.next_page_number(), 2)

        self.assertQuerysetEqual(all_languages[:1], response_languages_page_object.object_list)


@override_settings(RECENT_WORD_COUNT=3)
class WordDetailTests(TestCase):
    """
    Tests `word_detail` view
    URL: /dictionary/words/<int: word_id>
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

        for i in range(stg.PAGINATOR_PER_PAGE + 1):
            Word.objects.create(word=f"Word{ i } U{ cls.user1 }",
                                user=cls.user1,
                                word_language=cls.language1,
                                description=f'Word\'s{ i } description'
                                )

            Word.objects.create(word=f"Word{ i } U{ cls.user2 }",
                                user=cls.user2,
                                word_language=cls.language2,
                                description=f'Word\'s{ i } description'
                                )

        word1 = Word.objects.get(id=1)
        word2 = Word.objects.get(id=2)
        cls.translation1 = Translation(word=word1, user=cls.user1, translation_language=cls.language1, translation='testtranslation1')
        cls.translation2 = Translation(word=word1, user=cls.user1, translation_language=cls.language1, translation='testtranslation2')
        cls.translation3 = Translation(word=word1, user=cls.user1, translation_language=cls.language2, translation='testtranslation3')
        cls.translation4 = Translation(word=word2, user=cls.user2, translation_language=cls.language1, translation='testtranslation4')

        cls.hint1 = Hint(word=word1, user=cls.user1, hint='testhint1')
        cls.hint2 = Hint(word=word1, user=cls.user1, hint='testhint2')
        cls.hint3 = Hint(word=word2, user=cls.user2, hint='testhint3')


    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:word_detail', args=[1,]))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:word_detail", args=[1,]) }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:word_detail', args=[1,]))

        self.assertEqual(response.status_code, 200)

    def test_raises_404_if_word_does_not_exist(self):
        """Test if a 404 error is raised if the word does not exist"""

        response = self.client.get(reverse('dictionary:word_detail', args=[999,]))

        self.assertEqual(response.status_code, 404)

    def test_raises_permission_denied_if_word_created_by_other_user(self):
        """Test if a `PermissionDenied` error is raised if the word is created by another user"""

        response = self.client.get(reverse('dictionary:word_detail', args=[2,]))
        self.assertEqual(response.status_code, 403)

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:word_detail', args=[1,]))

        self.assertTemplateUsed(response, 'dictionary/word_detail.html')

    def test_context(self):
        """Test if context contains correct values"""

        response = self.client.get(reverse('dictionary:word_detail', args=[1,]))

        word = Word.objects.get(id=1)
        translations = Translation.objects.filter(word=word, user=word.user)
        hints = Hint.objects.filter(word=word, user=word.user)

        response_word = response.context['word']
        response_translations = response.context['translations']
        response_hints = response.context['hints']

        self.assertEqual(response_word, word)
        self.assertQuerysetEqual(response_translations, translations)
        self.assertQuerysetEqual(response_hints, hints)


@override_settings(RECENT_WORD_COUNT=3)
class LanguageDetailTests(TestCase):
    """
    Tests `language_detail` view
    URL: /dictionary/languages/<int: language_id>
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

        for i in range(stg.PAGINATOR_PER_PAGE + 1):
            Word.objects.create(word=f"Word{ i } U{ cls.user1 }",
                                user=cls.user1,
                                word_language=cls.language1,
                                description=f'Word\'s{ i } description'
                                )

            Word.objects.create(word=f"Word{ i } U{ cls.user2 }",
                                user=cls.user2,
                                word_language=cls.language2,
                                description=f'Word\'s{ i } description'
                                )

        word1 = Word.objects.get(id=1)
        word2 = Word.objects.get(id=2)
        cls.translation1 = Translation(word=word1, user=cls.user1, translation_language=cls.language1, translation='testtranslation1')
        cls.translation2 = Translation(word=word1, user=cls.user1, translation_language=cls.language1, translation='testtranslation2')
        cls.translation3 = Translation(word=word1, user=cls.user1, translation_language=cls.language2, translation='testtranslation3')
        cls.translation4 = Translation(word=word2, user=cls.user2, translation_language=cls.language1, translation='testtranslation4')

        cls.hint1 = Hint(word=word1, user=cls.user1, hint='testhint1')
        cls.hint2 = Hint(word=word1, user=cls.user1, hint='testhint2')
        cls.hint3 = Hint(word=word2, user=cls.user2, hint='testhint3')


    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:language_detail', args=[1,]))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:language_detail", args=[1,]) }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:language_detail', args=[1,]))

        self.assertEqual(response.status_code, 200)

    def test_raises_404_if_word_does_not_exist(self):
        """Test if a 404 error is raised if the element does not exist"""

        response = self.client.get(reverse('dictionary:language_detail', args=[999,]))

        self.assertEqual(response.status_code, 404)

    def test_raises_permission_denied_if_word_created_by_other_user(self):
        """Test if a `PermissionDenied` error is raised if the element is created by another user"""

        response = self.client.get(reverse('dictionary:language_detail', args=[3,]))
        self.assertEqual(response.status_code, 403)

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:language_detail', args=[1,]))

        self.assertTemplateUsed(response, 'dictionary/language_detail.html')

    def test_context(self):
        """Test if context contains correct values"""

        response = self.client.get(reverse('dictionary:language_detail', args=[1,]))
        response_language = response.context['language']
        language = Language.objects.get(id=1)

        self.assertEqual(response_language, language)


class WordAddTests(TestCase):
    """
    Tests `add_word` view
    URL: words/add/
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:add_word'))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:add_word") }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:add_word'))

        self.assertEqual(response.status_code, 200)

    def test_add_element_with_correct_values(self):
        """Test if a an element is added correctly"""

        response = self.client.post(
            reverse('dictionary:add_word'),
            data={
                'word': 'bus',
                'user': self.user1.pk,
                'word_language': self.language1.pk,
                'description': 'test description',
                'hint': 'test hint',
                'translation_language': self.language2.pk,
                'translation': 'автобус'
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dictionary:words_list"), target_status_code=200)

        # Check that objects were created
        created_word = None
        created_hint = None
        created_translation = None

        try:
            created_word = Word.objects.get(
                word='bus',
                user=self.user1,
                word_language=self.language1,
                description='test description',
            )

            created_hint = Hint.objects.get(
                word=created_word,
                user=self.user1,
                hint='test hint',
            )

            created_translation = Translation.objects.get(
                word=created_word,
                user=self.user1,
                translation_language=self.language2,
                translation='автобус',
            )

        except ObjectDoesNotExist:
            pass


        self.assertIsNotNone(created_word)
        self.assertIsNotNone(created_hint)
        self.assertIsNotNone(created_translation)

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:add_word'))

        self.assertTemplateUsed(response, 'dictionary/add_word.html')


class LanguageAddTests(TestCase):
    """
    Tests `add_language` view
    URL: languages/add/
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:add_language'))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:add_language") }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:add_language'))

        self.assertEqual(response.status_code, 200)

    def test_add_element_with_correct_values(self):
        """Test if a an element is added correctly"""

        response = self.client.post(
            reverse('dictionary:add_language'),
            data={
                'language_name': 'Hindi',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dictionary:languages_list"), target_status_code=200)

        # Check that objects were created
        created_language = None

        try:
            created_language = Language.objects.get(
                language_name='Hindi',
                user=self.user1,
            )

        except ObjectDoesNotExist:
            pass

        self.assertIsNotNone(created_language)

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:add_language'))

        self.assertTemplateUsed(response, 'dictionary/add_language.html')


@override_settings(PAGINATOR_PER_PAGE=3)
class WordEditTests(TestCase):
    """
    Tests `edit_word` view
    URL: words/edit/<int:word_id>
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

        for i in range(stg.PAGINATOR_PER_PAGE + 1):
            Word.objects.create(word=f"Word{ i } U{ cls.user1 }",
                                user=cls.user1,
                                word_language=cls.language1,
                                description=f'Word\'s{ i } description'
                                )

            Word.objects.create(word=f"Word{ i } U{ cls.user2 }",
                                user=cls.user2,
                                word_language=cls.language2,
                                description=f'Word\'s{ i } description'
                                )

        word1 = Word.objects.get(id=1)
        word2 = Word.objects.get(id=2)
        cls.translation1 = Translation.objects.create(word=word1, user=cls.user1, translation_language=cls.language1, translation='testtranslation1')
        cls.translation4 = Translation.objects.create(word=word2, user=cls.user2, translation_language=cls.language1, translation='testtranslation4')

        cls.hint1 = Hint.objects.create(word=word1, user=cls.user1, hint='testhint1')
        cls.hint3 = Hint.objects.create(word=word2, user=cls.user2, hint='testhint3')

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:edit_word', args=[1,]))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:edit_word", args=[1,]) }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:edit_word', args=[1,]))

        self.assertEqual(response.status_code, 200)

    def test_add_element_with_correct_values(self):
        """Test if a an element is added correctly"""

        response = self.client.get(reverse('dictionary:edit_word', args=[1,]))

        word_form = response.context['word_form']
        hint_form = response.context['hint_form']
        translation_form = response.context['translation_form']

        word_form_data = word_form.initial
        hint_form_data = hint_form.initial
        translation_form_data = translation_form.initial

        word_form_data['word'] = 'new_word'
        hint_form_data['hint'] = 'new_hint'
        translation_form_data['translation'] = 'new_translation'

        data = {**word_form_data, **hint_form_data, **translation_form_data}

        response = self.client.post(reverse('dictionary:edit_word', args=[1,]), data, follow=True)

        self.assertRedirects(response, reverse("dictionary:word_detail", args=[1,]), target_status_code=200)

        word = Word.objects.get(id=1, user=self.user1)
        hint = Hint.objects.get(id=1, user=self.user1)
        translation = Translation.objects.get(id=1, user=self.user1)

        self.assertEqual(word.word, 'new_word')
        self.assertEqual(hint.hint, 'new_hint')
        self.assertEqual(translation.translation, 'new_translation')

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:edit_word', args=[1,]))

        self.assertTemplateUsed(response, 'dictionary/add_word.html')


class LanguageEditTests(TestCase):
    """
    Tests `edit_language` view
    URL: languages/edit/<int:language_id>
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:edit_language', args=[1,]))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:edit_language", args=[1,]) }', target_status_code=200)

    def test_response(self):
        """Test if all responce details are correct (eg. status codes, redirects)"""

        response = self.client.get(reverse('dictionary:edit_language', args=[1,]))

        self.assertEqual(response.status_code, 200)

    def test_add_element_with_correct_values(self):
        """Test if a an element is added correctly"""

        response = self.client.get(reverse('dictionary:edit_language', args=[1,]))

        language_form = response.context['language_form']
        language_form_data = language_form.initial
        language_form_data['language_name'] = 'new_language'

        data = {**language_form_data}

        response = self.client.post(reverse('dictionary:edit_language', args=[1,]), data, follow=True)

        self.assertRedirects(response, reverse("dictionary:language_detail", args=[1,]), target_status_code=200)

        language = Language.objects.get(id=1, user=self.user1)

        self.assertEqual(language.language_name, 'new_language')

    def test_template(self):
        """Test if a required template is used"""

        response = self.client.get(reverse('dictionary:edit_language', args=[1,]))

        self.assertTemplateUsed(response, 'dictionary/add_language.html')


@override_settings(PAGINATOR_PER_PAGE=3)
class WordDeleteTests(TestCase):
    """
    Tests `delete_word` view
    URL: words/delete/<int:word_id>
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)
        
        for i in range(stg.PAGINATOR_PER_PAGE + 1):
            Word.objects.create(word=f"Word{ i } U{ cls.user1 }",
                                user=cls.user1,
                                word_language=cls.language1,
                                description=f'Word\'s{ i } description'
                                )

            Word.objects.create(word=f"Word{ i } U{ cls.user2 }",
                                user=cls.user2,
                                word_language=cls.language2,
                                description=f'Word\'s{ i } description'
                                )

        word1 = Word.objects.get(id=1)
        word2 = Word.objects.get(id=5)
        cls.translation1 = Translation.objects.create(word=word1, user=cls.user1, translation_language=cls.language1, translation='testtranslation1')
        cls.translation4 = Translation.objects.create(word=word2, user=cls.user2, translation_language=cls.language1, translation='testtranslation4')

        cls.hint1 = Hint.objects.create(word=word1, user=cls.user1, hint='testhint1')
        cls.hint3 = Hint.objects.create(word=word2, user=cls.user2, hint='testhint3')


    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:delete_word', args=[1,]))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:delete_word", args=[1,]) }', target_status_code=200)

    def test_deletes_invalid_user(self):
        """Test if invalid user tries to delete some users word"""
        
        response = self.client.get(reverse('dictionary:delete_word', args=[2,]))
        self.assertEqual(response.status_code, 403)

    def test_add_element_with_correct_values(self):
        """Test if a an element is added correctly"""

        response = self.client.get(reverse('dictionary:delete_word', args=[5,]))

        self.assertRedirects(response, reverse("dictionary:words_list"), target_status_code=200)

        self.assertRaises(Word.DoesNotExist, Word.objects.get, id=5)
        self.assertRaises(Hint.DoesNotExist, Hint.objects.get, id=2)
        self.assertRaises(Translation.DoesNotExist, Translation.objects.get, id=2)


@override_settings(PAGINATOR_PER_PAGE=3)
class LanguageDeleteTests(TestCase):
    """
    Tests `delete_language` view
    URL: languages/delete/<int:language_id>
    """

    @classmethod
    def setUpTestData(cls):
        """Setting up test data"""

        cls.client = Client()
        cls.user1 = User.objects.create_user(username='usrnm', password='psswd')
        cls.user2 = User.objects.create_user(username='usrnm2', password='psswd2')
        cls.language1 = Language.objects.create(user=cls.user1, language_name='English')
        cls.language2 = Language.objects.create(user=cls.user1, language_name='Russian')
        cls.language3 = Language.objects.create(user=cls.user2, language_name='Russian')

        cls.client.force_login(user=cls.user1)

    def setUp(self):
        """Login before each test start"""
        self.client.force_login(user=self.user1)

    @override_settings(LOGIN_URL='/login/')
    def test_logout_redirects(self):
        """Test if unauthorized user is redirected to the login page"""

        self.client.logout()
        response = self.client.get(reverse('dictionary:delete_language', args=[1,]))

        self.assertRedirects(response, f'/login/?next={ reverse("dictionary:delete_language", args=[1,]) }', target_status_code=200)

    def test_deletes_invalid_user(self):
        """Test if invalid user tries to delete some users word"""
        
        response = self.client.get(reverse('dictionary:delete_language', args=[3,]))
        self.assertEqual(response.status_code, 403)

    def test_add_element_with_correct_values(self):
        """Test if a an element is added correctly"""

        response = self.client.get(reverse('dictionary:delete_language', args=[2,]))

        self.assertRedirects(response, reverse("dictionary:languages_list"), target_status_code=200)

        self.assertRaises(Language.DoesNotExist, Language.objects.get, id=2)
