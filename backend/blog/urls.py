from django.conf import settings
from django.urls import path, include
from django.views.static import serve
from . import views

app_name = 'blog'

urlpatterns = [
    path('api/posts/', views.PostList.as_view(), name='post-list'),
    path('api/posts/<pk>/<slug>/', views.PostDetail.as_view(), name='post-detail'),
    path('api/like/', views.LikeView.as_view(), name='like'),
    path('api/tags/', views.TagList.as_view(), name='tag-list'),
    path('api/categories/', views.CategoryList.as_view(), name='category-list'),
    path('api/posts/simple_search', views.posts_simple_search, name='posts-simple-search'),
]