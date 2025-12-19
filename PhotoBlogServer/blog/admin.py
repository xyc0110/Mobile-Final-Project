from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_pinned', 'published_date')
    list_filter = ('is_pinned',)
    ordering = ('-is_pinned', '-published_date')