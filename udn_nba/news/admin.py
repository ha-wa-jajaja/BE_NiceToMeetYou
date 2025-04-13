from django.contrib import admin

from .models import Author, News, NewsSession

admin.site.register(News)
admin.site.register(NewsSession)
admin.site.register(Author)
