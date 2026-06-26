from django.contrib import admin
from .models import Profile, Article, Comment, Blog

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'created_at')
    search_fields = ('user__username', 'display_name')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'views', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at', 'author')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'rating', 'content_excerpt', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('content', 'user__username', 'article__title')

    def content_excerpt(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_excerpt.short_description = 'Nội dung'

admin.site.register(Blog)