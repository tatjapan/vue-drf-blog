import markdown
from django.db import models
from datetime import date
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.text import slugify
from markdown.extensions import Extension


class Tag(models.Model):
    """記事のタグ"""
    name = models.CharField('タグ名', max_length=255, unique=True)
    slug = models.SlugField(
        max_length=255, 
        unique=True,
        default='',
        null=True,
        blank=True,
        editable=True,
        allow_unicode=True,
    )

    def __str__(self):
        # 検索フォームやタグクラウドで、紐づいた記事数を表示する。post_countで動画数を保持。
        if hasattr(self, 'post_count'):
            return f'{self.name}({self.post_count})'
        else:
            return '{id}:{name}'.format(id=self.id, name=self.name)

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super(Tag, self).save(*args, **kwargs)


class Category(models.Model):
    """記事のカテゴリー。デフォルトのカテゴリーを関数でセット"""
    CATEGORY_TYPE = (
        (1, "main"),
        (2, "sub"),
    )
    name = models.CharField('カテゴリー名', max_length=100, unique=True, default='プログラミング')
    category_type = models.IntegerField(choices=CATEGORY_TYPE, verbose_name="カテゴリーレベル", help_text="カテゴリーレベル")
    parent_category = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='subcategories')
    slug = models.SlugField(
        max_length=100, 
        unique=True,
        default='',
        null=True,
        blank=True,
        editable=True,
        allow_unicode=True,
    )

    def __str__(self):
        if hasattr(self, 'post_count'):
            return f'{self.name}({self.post_count})'
        else:
            return '{id}:{name}'.format(id=self.id, name=self.name)
    
    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super(Category, self).save(*args, **kwargs)     

def get_or_create_default_category():
    category, _ = Category.objects.get_or_create(name='プログラミング', category_type=1)
    return category


class Post(models.Model):
    """記事"""
    title = models.CharField('タイトル', max_length=50)
    text = models.TextField('本文')
    thumbnail = models.ImageField('サムネイル', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='カテゴリー', null=True, blank=True, default=get_or_create_default_category)
    tags = models.ManyToManyField(Tag, verbose_name='タグ', blank=True)
    relation_posts = models.ManyToManyField('self', verbose_name='関連記事', blank=True)
    is_public = models.BooleanField('公開可能か?', default=True)
    """ Like """
    likes = models.IntegerField(verbose_name='いいね', default=0)
    """ SEOのmeta関連 """
    description = models.TextField('記事の説明（SEOのmeta関連）', max_length=130)
    keywords = models.CharField('記事のキーワード（SEOのmeta関連）', max_length=255, default='Dart,Flutter')
    viewnumber = models.IntegerField(verbose_name='閲覧数', validators=[MinValueValidator(0)], default=0)
    created_at = models.DateTimeField('作成日', default=timezone.now)
    updated_at = models.DateTimeField('更新日', default=timezone.now)
    
    def counter_today_unique(self):
        return Counter.objects.filter(post=self).values('ip_address', 'access_at').distinct()

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def text_to_html(self):
        return markdown.markdown(self.text, extensions=['markdown.extensions.extra', 'markdown.extensions.toc'])


class Counter(models.Model):
    """記事閲覧数のカウンター"""
    ip_address = models.GenericIPAddressField()
    access_at = models.DateField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return "{0},{1},{2}".format(self.ip_address, self.post, self.access_at)


class Like(models.Model):
    """記事「いいね」ボタン用モデル"""
    ip_address = models.GenericIPAddressField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like')

    def save(self, *args, **kwargs):
        try:
            self.post.likes += 1
            self.post.save()
            super(Like, self).save(*args, **kwargs)

        except IntegrityError:
            self.post.likes -= 1
            self.post.save()
            raise IntegrityError

    def __str__(self):
        return self.post.title