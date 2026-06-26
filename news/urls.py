from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.article_list, name='article_list'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/like/', views.like_article, name='like_article'),
    path('article/<slug:slug>/save/', views.save_article, name='save_article'),
    path('community/', views.blog_list, name='blog_list'),
    path('community/create/', views.blog_create, name='blog_create'),
    path('community/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('community/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    path('community/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
    path('search/', views.search_results, name='search_results'),
    path('saved/', views.saved_articles, name='saved_articles'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about, name='about'),

    path('ckeditor5/', include('django_ckeditor_5.urls')),

    path('assistant_response/', views.assistant_response, name='assistant_response'),
]
