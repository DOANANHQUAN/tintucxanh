"""
Django management command: seed dữ liệu Article từ RSS VnExpress.

CÀI ĐẶT
-------
pip install feedparser requests beautifulsoup4

ĐẶT FILE
--------
Copy file này vào:
    <news>/management/commands/seed_vnexpress.py

Nhớ tạo các file __init__.py rỗng (nếu chưa có):
    <tên_app>/management/__init__.py
    <tên_app>/management/commands/__init__.py


CÁCH DÙNG
---------
# Lấy 20 bài mới nhất, dùng user admin làm tác giả
python manage.py seed_vnexpress --author admin --limit 20

# Lấy theo 1 chuyên mục cụ thể (xem danh sách RSS tại https://vnexpress.net/rss)
python manage.py seed_vnexpress --url https://vnexpress.net/rss/cong-nghe.rss --limit 30

# Lấy nội dung đầy đủ của bài viết (scrape trang gốc) thay vì chỉ tóm tắt
python manage.py seed_vnexpress --full-content

# Cập nhật lại nội dung đầy đủ cho các bài đã seed trước đó (không tải lại ảnh)
python manage.py seed_vnexpress --url https://vnexpress.net/rss/the-gioi.rss --update-content

DANH SÁCH FLAG
--------------
--url             (str)   Mặc định: https://vnexpress.net/rss/tin-moi-nhat.rss
                  URL RSS feed cần lấy (đổi sang feed chuyên mục khác nếu muốn,
                  ví dụ the-gioi.rss, cong-nghe.rss, kinh-doanh.rss...).

--limit           (int)   Mặc định: 20
                  Số bài tối đa lấy từ feed mỗi lần chạy.

--author          (str)   Mặc định: user đầu tiên trong DB
                  Username sẽ gắn làm tác giả cho các bài viết được tạo.

--full-content    (cờ)    Mặc định: tắt
                  Vào trang gốc của từng bài để lấy nội dung đầy đủ, thay vì
                  chỉ lấy đoạn tóm tắt 1 câu trong RSS (chậm hơn vì phải tải
                  thêm trang).

--update-content  (cờ)    Mặc định: tắt
                  Với các bài đã tồn tại (trùng slug), cập nhật lại nội dung
                  đầy đủ thay vì bỏ qua — dùng để vá nội dung cho các bài đã
                  seed trước đó.

--featured-every  (int)   Mặc định: 0
                  Cứ mỗi N bài thì đánh dấu 1 bài is_featured=True.
                  0 = không đánh dấu bài nào.

--debug           (cờ)    Mặc định: tắt
                  In ra lý do cụ thể khi không lấy được ảnh hoặc không lấy
                  được nội dung đầy đủ (giúp chẩn đoán lỗi).

VÍ DỤ KẾT HỢP NHIỀU FLAG
------------------------
python manage.py seed_vnexpress \\
    --url https://vnexpress.net/rss/kinh-doanh.rss \\
    --limit 30 \\
    --author admin \\
    --full-content \\
    --featured-every 10 \\
    --debug
"""

import re
import time
from datetime import datetime, timezone as dt_timezone
from io import BytesIO

import feedparser
import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from news.models import Article

DEFAULT_FEED = "https://vnexpress.net/rss/tin-moi-nhat.rss"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://vnexpress.net/",
}


class Command(BaseCommand):
    help = "Seed dữ liệu Article từ RSS feed của VnExpress."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url", default=DEFAULT_FEED,
            help=f"URL RSS feed (mặc định: {DEFAULT_FEED})",
        )
        parser.add_argument(
            "--limit", type=int, default=20,
            help="Số bài tối đa cần seed (mặc định 20).",
        )
        parser.add_argument(
            "--author", default=None,
            help="Username sẽ gắn làm tác giả. Nếu bỏ trống sẽ dùng user đầu tiên trong hệ thống.",
        )
        parser.add_argument(
            "--full-content", action="store_true",
            help="Scrape luôn nội dung đầy đủ từ trang bài viết (chậm hơn).",
        )
        parser.add_argument(
            "--featured-every", type=int, default=0,
            help="Đánh is_featured=True cho mỗi N bài (0 = không đánh dấu bài nào).",
        )
        parser.add_argument(
            "--debug", action="store_true",
            help="In chi tiết lý do khi không lấy được ảnh.",
        )
        parser.add_argument(
            "--update-content", action="store_true",
            help="Với bài đã tồn tại (trùng slug), cập nhật lại nội dung đầy đủ thay vì bỏ qua.",
        )

    def handle(self, *args, **options):
        feed_url = options["url"]
        limit = options["limit"]
        full_content = options["full_content"]
        featured_every = options["featured_every"]
        debug = options["debug"]
        update_content = options["update_content"]

        author = self._get_author(options["author"])

        self.stdout.write(f"Đang tải RSS: {feed_url}")
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            raise CommandError(f"Không đọc được RSS feed: {feed.bozo_exception}")

        entries = feed.entries[:limit]
        self.stdout.write(f"Tìm thấy {len(entries)} bài, bắt đầu seed...")

        created_count = 0
        for i, entry in enumerate(entries, start=1):
            title = getattr(entry, "title", "").strip()
            if not title:
                continue

            slug = slugify(title)[:250]
            existing = Article.objects.filter(slug=slug).first()
            if existing:
                if update_content and getattr(entry, "link", None):
                    scraped = self._scrape_full_content(entry.link)
                    if scraped:
                        existing.content = scraped
                        existing.save(update_fields=["content"])
                        self.stdout.write(self.style.SUCCESS(f"  [updated] {title}"))
                    elif debug:
                        self.stdout.write(self.style.WARNING(f"    -> không lấy được nội dung đầy đủ: {title}"))
                else:
                    self.stdout.write(f"  [skip] đã tồn tại: {title}")
                continue

            summary_html = getattr(entry, "summary", "") or getattr(entry, "description", "")
            content_text = self._clean_html(summary_html)

            if full_content and getattr(entry, "link", None):
                scraped = self._scrape_full_content(entry.link)
                if scraped:
                    content_text = scraped

            tags = self._extract_tags(entry)
            image_url = self._extract_image_url(entry, summary_html)
            if not image_url and getattr(entry, "link", None):
                image_url = self._scrape_og_image(entry.link)
            published_dt = self._parse_published(entry)

            article = Article(
                title=title,
                slug=slug,
                content=content_text or title,
                author=author,
                tags=tags,
                is_featured=bool(featured_every) and i % featured_every == 0,
            )

            if image_url:
                image_content, err = self._download_image(image_url)
                if image_content:
                    ext = image_url.split(".")[-1].split("?")[0][:4] or "jpg"
                    article.thumbnail.save(
                        f"{slug}.{ext}", ContentFile(image_content), save=False
                    )
                elif debug:
                    self.stdout.write(self.style.WARNING(f"    -> lỗi tải ảnh ({image_url}): {err}"))
            elif debug:
                self.stdout.write(self.style.WARNING("    -> không tìm thấy URL ảnh trong RSS/og:image"))

            if not article.thumbnail:
                # Article.thumbnail không cho null, nhưng nếu không tải được ảnh
                # thì bỏ qua bài này để tránh lỗi khi save().
                self.stdout.write(f"  [skip] không có ảnh: {title}")
                continue

            article.save()

            # auto_now_add ghi đè created_at lúc save(), nên cập nhật lại
            # ngày đăng thật của bài viết bằng update() sau khi đã tạo.
            if published_dt:
                Article.objects.filter(pk=article.pk).update(created_at=published_dt)

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"  [ok] {title}"))

            time.sleep(0.3)  # tránh spam server VnExpress

        self.stdout.write(self.style.SUCCESS(f"\nHoàn tất: đã tạo {created_count} bài viết."))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_author(self, username):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f"Không tìm thấy user '{username}'.")
        author = User.objects.first()
        if not author:
            raise CommandError("Chưa có user nào trong hệ thống. Tạo superuser trước (python manage.py createsuperuser).")
        return author

    def _clean_html(self, html):
        if not html:
            return ""
        text = BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()
        return re.sub(r"\n{3,}", "\n\n", text)

    def _extract_tags(self, entry):
        cats = [t.term.strip() for t in getattr(entry, "tags", []) if getattr(t, "term", None)]
        return ", ".join(cats[:5]) if cats else "Tin tức"

    def _extract_image_url(self, entry, summary_html):
        # 1) enclosure
        for enc in getattr(entry, "enclosures", []):
            href = enc.get("href")
            if href:
                return href
        # 2) media_content / media_thumbnail (nếu feed có namespace media)
        for key in ("media_content", "media_thumbnail"):
            media = getattr(entry, key, None)
            if media:
                url = media[0].get("url")
                if url:
                    return url
        # 3) tìm <img src="..."> trong description
        if summary_html:
            match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary_html)
            if match:
                return match.group(1)
        return None

    def _scrape_og_image(self, article_url):
        try:
            resp = requests.get(article_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", property="og:image")
        if meta and meta.get("content"):
            return meta["content"]
        return None

    def _download_image(self, url):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if "image" not in content_type and len(resp.content) < 1000:
                return None, f"response không phải ảnh (Content-Type: {content_type})"
            return BytesIO(resp.content).read(), None
        except requests.RequestException as e:
            return None, str(e)

    def _scrape_full_content(self, article_url):
        try:
            resp = requests.get(article_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")

        # Cách 1: khối nội dung chính có class fck_detail (cấu trúc phổ biến của VnExpress)
        body = soup.find("article", class_="fck_detail") or soup.find("div", class_="fck_detail")
        if body:
            paragraphs = [p.get_text(strip=True) for p in body.find_all("p")]
            text = "\n\n".join(p for p in paragraphs if p)
            if text:
                return text

        # Cách 2: các đoạn văn có class "Normal" (class hay dùng cho đoạn văn bài viết)
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p", class_="Normal")]
        text = "\n\n".join(p for p in paragraphs if p)
        if text:
            return text

        # Cách 3: lấy mọi <p> trong <article> bất kỳ trên trang
        article_tag = soup.find("article")
        if article_tag:
            paragraphs = [p.get_text(strip=True) for p in article_tag.find_all("p")]
            text = "\n\n".join(p for p in paragraphs if p)
            if text:
                return text

        return None

    def _parse_published(self, entry):
        parsed = getattr(entry, "published_parsed", None)
        if not parsed:
            return None
        return datetime(*parsed[:6], tzinfo=dt_timezone.utc)