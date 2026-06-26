import json
import os

from certifi import contents
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
import requests
from .models import Article, Blog, Comment, Profile
from .forms import RegisterForm, ProfileForm, UserForm, CommentForm
from django.http import JsonResponse
from openai import OpenAI
from google import genai

def get_popular_tags():
    # Helper to get all tags and count frequency
    all_articles = Article.objects.all()
    tag_counts = {}
    for art in all_articles:
        for tag in art.tag_list:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    # Sort by frequency
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return [t[0] for t in sorted_tags[:10]]

def home(request):
    articles = Article.objects.all()
    
    # Hero Banner: Lấy 1 tin nổi bật mới nhất
    hero_article = articles.filter(is_featured=True).first()
    if not hero_article:
        hero_article = articles.first()
        
    # Breaking News: 3 tin mới nhất
    breaking_news = articles.order_by('-created_at')[:3]
    
    # Tin nổi bật khác: 4 tin nổi bật (loại trừ hero_article)
    featured_news = articles.filter(is_featured=True)
    if hero_article:
        featured_news = featured_news.exclude(id=hero_article.id)
    featured_news = featured_news[:4]
    
    # Tin mới nhất: 6 tin
    latest_news = articles.order_by('-created_at')[:6]
    
    # Tin xem nhiều: 5 tin
    most_viewed = articles.order_by('-views')[:5]
    
    # Tags phổ biến
    popular_tags = get_popular_tags()

    api_key = os.environ.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Thu Dau Mot,VN&appid={api_key}&units=metric&lang=vi"

    response = requests.get(url)
    data = response.json()

    context = {
        'hero_article': hero_article,
        'breaking_news': breaking_news,
        'featured_news': featured_news,
        'latest_news': latest_news,
        'most_viewed': most_viewed,
        'popular_tags': popular_tags,
        # Weather data
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
    }
    return render(request, 'home.html', context)

def article_list(request):
    articles = Article.objects.all()
    tag_filter = request.GET.get('tag')
    if tag_filter:
        articles = [art for art in articles if tag_filter in art.tag_list]
    
    most_viewed = Article.objects.order_by('-views')[:5]
    popular_tags = get_popular_tags()

    context = {
        'articles': articles,
        'tag_filter': tag_filter,
        'most_viewed': most_viewed,
        'popular_tags': popular_tags,
    }
    return render(request, 'article_list.html', context)

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    # Tăng lượt xem thực tế
    article.views += 1
    article.save(update_fields=['views'])
    
    # Bình luận
    comments = article.comments.all()
    comment_form = CommentForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            messages.success(request, 'Bình luận của bạn đã được đăng!')
            return redirect('article_detail', slug=article.slug)

    # Tin liên quan: cùng tag
    related_articles = []
    if article.tag_list:
        query = Q()
        for tag in article.tag_list:
            query |= Q(tags__icontains=tag)
        related_articles = Article.objects.filter(query).exclude(id=article.id).distinct()[:3]
    
    most_viewed = Article.objects.order_by('-views')[:5]
    popular_tags = get_popular_tags()

    is_liked = False
    is_saved = False
    if request.user.is_authenticated:
        is_liked = article.likes.filter(id=request.user.id).exists()
        is_saved = article.saves.filter(id=request.user.id).exists()

    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'related_articles': related_articles,
        'most_viewed': most_viewed,
        'popular_tags': popular_tags,
        'is_liked': is_liked,
        'is_saved': is_saved,
    }
    return render(request, 'article_detail.html', context)

def search_results(request):
    query = request.GET.get('q', '')
    articles = Article.objects.all()
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()
        
    most_viewed = Article.objects.order_by('-views')[:5]
    popular_tags = get_popular_tags()

    context = {
        'query': query,
        'articles': articles,
        'most_viewed': most_viewed,
        'popular_tags': popular_tags,
    }
    return render(request, 'search_results.html', context)

def blog_list(request):
    blogs = Blog.objects.all()
    most_viewed = Article.objects.order_by('-views')[:5]
    popular_tags = get_popular_tags()
    sort = None

    if request.user.is_authenticated:
        if request.GET.get('user') == str(request.user.id):
            user_id = request.user.id
            blogs = blogs.filter(author__id=user_id)
            sort = 'user'

    context = {
        'blogs': blogs,
        'most_viewed': most_viewed,
        'popular_tags': popular_tags,
        'sort': sort,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog/blog_detail.html', {'blog': blog, 'slug': slug})

def blog_create(request):
    if not request.user.is_authenticated:
        messages.error(request, "Bạn cần đăng nhập để tạo bài viết cộng đồng.")
        return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        thumbnail = request.FILES.get('thumbnail')

        if title and content and thumbnail:
            blog = Blog.objects.create(
                title=title,
                content=content,
                thumbnail=thumbnail,
                author=request.user,
            )
            messages.success(request, "Blog đã được tạo thành công.")
            return redirect('blog_list')
        else:
            messages.error(request, "Vui lòng điền đầy đủ thông tin và tải lên ảnh đại diện.")
    return render(request, 'blog/blog_form.html', {'type': 'create'})

def blog_edit(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        thumbnail = request.FILES.get('thumbnail')

        if title and content:
            blog.title = title
            blog.content = content
            if thumbnail:
                blog.thumbnail = thumbnail
            blog.save()
            messages.success(request, "Blog đã được cập nhật thành công.")
            return redirect('blog_detail', slug=blog.slug)
        else:
            messages.error(request, "Vui lòng điền đầy đủ thông tin.")
    return render(request, 'blog/blog_form.html', {'blog': blog, 'type': 'edit'})

def blog_delete(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.user != blog.author:
        messages.error(request, "Bạn không có quyền xóa bài viết này.")
        return redirect('blog_list')
    if request.method == 'POST':
        blog.delete()
        messages.success(request, "Bài viết đã được xóa thành công.")
        return redirect('blog_list')
    return render(request, 'blog/blog_delete.html', {'blog': blog})

@login_required
def like_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.likes.filter(id=request.user.id).exists():
        article.likes.remove(request.user)
        messages.info(request, "Đã bỏ thích bài viết.")
    else:
        article.likes.add(request.user)
        messages.success(request, "Đã thích bài viết.")
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('article_detail', slug=slug)

@login_required
def save_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.saves.filter(id=request.user.id).exists():
        article.saves.remove(request.user)
        messages.info(request, "Đã bỏ lưu bài viết.")
    else:
        article.saves.add(request.user)
        messages.success(request, "Đã lưu bài viết vào danh sách đọc sau.")
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('article_detail', slug=slug)

@login_required
def saved_articles(request):
    articles = request.user.saved_articles.all()
    most_viewed = Article.objects.order_by('-views')[:5]
    popular_tags = get_popular_tags()
    
    context = {
        'articles': articles,
        'most_viewed': most_viewed,
        'popular_tags': popular_tags,
    }
    return render(request, 'saved_articles.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            login(request, user)
            messages.success(request, "Đăng ký tài khoản thành công!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Chào mừng {username} đã quay trở lại!")
                return redirect('home')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất thành công.")
    return redirect('home')

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Cập nhật hồ sơ cá nhân thành công!")
                return redirect('profile')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Đổi mật khẩu thành công!")
                return redirect('profile')
            else:
                messages.error(request, "Vui lòng sửa các lỗi bên dưới để đổi mật khẩu.")
    
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=profile)
    password_form = PasswordChangeForm(request.user)
    
    liked_articles = request.user.liked_articles.all()
    saved_articles_list = request.user.saved_articles.all()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'liked_articles': liked_articles,
        'saved_articles_list': saved_articles_list,
    }
    return render(request, 'profile.html', context)

def about(request):
    return render(request, 'about.html')

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def assistant_response(request):
    try:
        print("REQUEST RECEIVED")

        data = json.loads(request.body)
        print(data)

        user_input = data.get("message")
        print("MESSAGE:", user_input)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_input,
            config={
                "system_instruction": """
                    Bạn tên là Lữ Minh Khang, một học sinh 15 tuổi.
                    Đóng giả làm tsundere.
                    Nhiệm vụ của bạn là trò chuyện, kết thân với người dùng.
                """
            }
        )

        return JsonResponse({
            "reply": response.text,
        })

    except Exception as e:
        print("ERROR:", str(e))
        return JsonResponse({
            "error": str(e)
        }, status=500)