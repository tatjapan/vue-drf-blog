from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .get_ip import get_client_ip
from .models import Post, Tag, Like, Category

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields =  "__all__"


class CategorySerializer2(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        

class CategorySerializer(serializers.ModelSerializer):
    subcategories = CategorySerializer2(many=True)
    class Meta:
        model = Category
        fields = "__all__"
    

class TagWithPostCountSerializer(serializers.ModelSerializer):
    """紐づく記事の数を表示するタグシリアライザー"""
    post_count = serializers.IntegerField(
        source = 'post_set.count',
        read_only = True
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'post_count')


class CategoryWithPostCountSerializer(serializers.ModelSerializer):
    """紐づく記事の数を表示するタグシリアライザー"""
    post_count = serializers.IntegerField(
        source = 'post_set.count',
        read_only = True
    )

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'post_count')


class BasePostSerializer(serializers.ModelSerializer):
    """フィールド数を一部限定した基本となるシリアライザー"""
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer()
    view_counts = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'tags',
            'category',
            'thumbnail',
            'view_counts',
            'likes',
            'created_at',
            'updated_at',
            'slug',
        )

    def get_view_counts(self, obj):
        return obj.counter_today_unique().all().count()


class PostSerializer(serializers.ModelSerializer):
    """フィールド数を限定しないシリアライザー"""
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer()
    relation_posts = BasePostSerializer(many=True, read_only=True)
    view_counts = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'text_to_html',
            'tags',
            'category',
            'thumbnail',
            'view_counts',
            'likes',
            'is_liked',
            'relation_posts',
            'created_at',
            'updated_at',
            'slug',
        )

    def get_view_counts(self, obj):
        return obj.counter_today_unique().all().count()

    def get_is_liked(self, obj):
        request = self.context['request']
        if Like.objects.filter(post=obj, ip_address=get_client_ip(request)).exists():
            return True
        else:
            return False


class LikeSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        post = get_object_or_404(Post, id=validated_data["post_id"])
        like = Like()
        like.post = post
        try:
            like.save()
        except IntegrityError:
            return like
        return like

    class Meta:
        model = Like
        exclude = ("id", "ip_address", "post")