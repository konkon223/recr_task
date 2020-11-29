from django.contrib import admin
from .models import Movie, Comment


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "data")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("movie", "body", "created")
    fields = ("created",)
