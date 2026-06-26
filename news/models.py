from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, display_name=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    thumbnail = models.ImageField(upload_to='thumbnails/', verbose_name="Ảnh đại diện")
    content = models.TextField(verbose_name="Nội dung")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tác giả")
    tags = models.CharField(max_length=200, help_text="Phân tách các tag bằng dấu phẩy (ví dụ: Công nghệ, AI, Game)")
    views = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    is_featured = models.BooleanField(default=False, verbose_name="Tin nổi bật")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True, verbose_name="Lượt thích")
    saves = models.ManyToManyField(User, related_name='saved_articles', blank=True, verbose_name="Đã lưu")

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    @property
    def average_rating(self):
        comments = self.comments.all()
        if not comments:
            return 0
        total = sum(c.rating for c in comments)
        return round(total / len(comments), 1)

    @property
    def average_rating_stars(self):
        avg = self.average_rating
        return range(int(avg))

    @property
    def average_rating_empty_stars(self):
        avg = self.average_rating
        return range(5 - int(avg))
    
class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', verbose_name="Ảnh đại diện")
    content = CKEditor5Field('Nội dung', config_name='extends', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tác giả")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name="Bài viết")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người dùng")
    content = models.TextField(verbose_name="Bình luận")
    rating = models.PositiveIntegerField(default=5, choices=[(i, f"{i} Sao") for i in range(1, 6)], verbose_name="Đánh giá sao")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.article.title[:20]}"

    @property
    def rating_stars(self):
        return range(self.rating)

    @property
    def rating_empty_stars(self):
        return range(5 - self.rating)
