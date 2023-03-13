from django.urls import path
from . import views

app_name = 'dictionary'
urlpatterns = [
    # Index
    path('', views.index, name='index'),

    # List views
    path('words/', views.words_list, name='words_list'),
    path('languages/', views.languages_list, name='languages_list'),

    # Detail views
    path('words/<int:word_id>/', views.word_detail, name='word_detail'),
    path('languages/<int:language_id>/', views.language_detail, name='language_detail'),

    # Add items views
    path('words/add/', views.add_word, name='add_word'),
    path('words/add/from_file/', views.add_words_from_file, name='add_words_from_file'),
    path('languages/add/', views.add_language, name='add_language'),

    # Edit items views
    path('words/edit/<int:word_id>', views.edit_word, name='edit_word'),
    path('languages/edit/<int:language_id>', views.edit_language, name='edit_language'),

    # Delete items views
    path('words/delete/<int:word_id>', views.delete_word, name='delete_word'),
    path('languages/delete/<int:language_id>', views.delete_language, name='delete_language'),
]