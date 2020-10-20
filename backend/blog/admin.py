from django import forms
from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import Post, Tag, Category


class SuggestPostWidget(forms.SelectMultiple):
    """関連記事の作成・更新をカスタマイズ"""
    template_name = 'blog/widgets/suggest.html'

    class Media:
        css = {
            'all': [
                'blog/css/admin_post_form.css',

            ]
        }
        js = ['blog/js/suggest.js']

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' suggest'
        else:
            self.attrs['class'] = 'suggest'

class AdminPostCreateForm(forms.ModelForm):
    """記事の作成・更新フォーム"""

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': '[TOC]\n\n## 記事本文の概要\n以降に記載'}),
            'relation_posts': SuggestPostWidget(attrs={'data-url': reverse_lazy('blog:posts-simple-search')}),
        }


class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text')
    list_display = ['title', 'is_public', 'updated_at', 'created_at']
    list_filter = ['is_public', 'tags', 'category', 'created_at', 'updated_at']
    form = AdminPostCreateForm


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Category)