from django.conf import settings
from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.views import generic
from rest_framework import generics, response, status, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .get_ip import get_client_ip
from .models import Post, Tag, Like, Counter, Category
from .serializers import BasePostSerializer, PostSerializer, TagWithPostCountSerializer, LikeSerializer, CategorySerializer, CategoryWithPostCountSerializer

class Pagination(PageNumberPagination):
    page_size = 12

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'post_list': data,
        })


class PostList(generics.ListAPIView):
    queryset = Post.objects.prefetch_related('tags', 'category').order_by('-updated_at')
    serializer_class = BasePostSerializer
    pagination_class = Pagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        params = self.request.query_params

        keyword = params.get('keyword', None)
        if keyword:
            # スペース区切りでの複数キーワード検索に対応
            for k in keyword.split():
                queryset = queryset.filter(Q(title__icontains=k) | Q(description__icontains=k) | Q(text__icontains=k))

        tags = params.getlist('tag', None)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags=tag)

        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        return queryset


class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.prefetch_related('relation_posts__tags', 'relation_posts__category')
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        counter = Counter(ip_address=get_client_ip(request), post=obj)
        counter.save()
        return super().retrieve(request, *args, **kwargs)


class TagList(generics.ListAPIView):
    queryset = Tag.objects.prefetch_related('post_set').order_by('name')
    serializer_class = TagWithPostCountSerializer


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.prefetch_related('post_set').order_by('name')
    serializer_class = CategoryWithPostCountSerializer


@api_view()
def posts_simple_search(request):
    """キーワードで絞り込んだ記事の一覧を返す。管理画面での関連記事サジェストに使用"""
    keyword = request.GET.get('keyword')
    if keyword:
        post_list = [{'pk': post.pk, 'name': post.title} for post in Post.objects.filter(title__icontains=keyword)]
    else:
        post_list = []
    return Response({'object_list': post_list})


class LikeView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            created_instance = serializer.create(validated_data=request.data)
            created_instance.ip_address = get_client_ip(request)
            
            try:
                created_instance.save()

            except IntegrityError:
                return Response(
                    { "message": "既に「いいね」済みです。" },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                { "message": "この記事に「いいね」しました。" },
                status=status.HTTP_200_OK
            )