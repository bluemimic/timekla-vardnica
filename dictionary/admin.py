from django.contrib import admin
from .models import *

admin.site.register(Language)
admin.site.register(Word)
admin.site.register(Hint)
admin.site.register(Translation)