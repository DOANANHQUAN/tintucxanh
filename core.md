# NEWS_WEBSITE_PROMPT.md

## Vai trò

Bạn là Senior Django Developer với hơn 10 năm kinh nghiệm.

Hãy tạo một dự án website tin tức hoàn chỉnh bằng Django theo mô hình MTV (Model - Template - View).

Mục tiêu là tạo KHUNG DỰ ÁN đầy đủ để phục vụ học tập, không cần các chức năng nâng cao như SEO, REST API hay triển khai thực tế.

---

# Thông tin dự án

Tên website:

Tin Tức Xanh

Loại website:

- Tin tức tổng hợp
- Công nghệ
- Thể thao
- Game
- Giáo dục

Ngôn ngữ:

- Python
- Django
- HTML
- CSS
- Bootstrap 5
- SQLite

Kiến trúc:

- MTV (Model Template View)
- Chỉ sử dụng Django Template
- Không dùng React
- Không dùng REST API

---

# Yêu cầu cấu trúc dự án

Chỉ sử dụng một app duy nhất:

news

Tạo cấu trúc thư mục đầy đủ:

project/
│
├── news/
├── static/
├── media/
├── templates/
│
├── manage.py
│
└── settings.py

---

# Thiết kế giao diện

## Màu sắc

Primary Color:

#1E40AF

Secondary Color:

#E0F2FE

Accent Color:

#F97316

## Phong cách

- Hiện đại
- Chuyên nghiệp
- Tin cậy
- Giao diện sạch
- Nhiều khoảng trắng
- Dễ đọc

## Font

Heading:

Inter

Body:

Roboto

## Framework

Bootstrap 5

---

# Responsive

Chỉ cần tối ưu cho Desktop.

---

# Chức năng tài khoản

Cho phép:

- Đăng ký
- Đăng nhập
- Đăng xuất

Hỗ trợ:

- Email + Password
- Google Login

---

# Hồ sơ người dùng

Mỗi người dùng có:

- Avatar
- Tên hiển thị
- Email

Người dùng có thể:

- Xem danh sách bài viết đã thích
- Xem danh sách bài viết đã lưu
- Đổi mật khẩu

---

# Model User Profile

Tạo model Profile:

- user
- avatar
- display_name
- created_at

---

# Model Bài Viết

Tạo model Article:

- title
- slug
- thumbnail
- content
- author
- tags
- views
- is_featured
- created_at
- updated_at

Giải thích rõ kiểu dữ liệu phù hợp cho từng trường.

---

# Chức năng bài viết

Mỗi bài viết có:

- Tiêu đề
- Ảnh đại diện
- Nội dung
- Tags
- Tác giả
- Ngày đăng

Cho phép:

- Xem chi tiết bài viết
- Xem danh sách bài viết
- Tìm kiếm bài viết
- Like bài viết
- Lưu bài viết

---

# Tin nổi bật

Admin có thể:

- Đánh dấu bài viết nổi bật

Trang chủ phải hiển thị:

- Tin nổi bật

---

# Tin xem nhiều

Mỗi khi người dùng truy cập bài viết:

views tăng lên.

Trang chủ hiển thị:

- Top bài viết xem nhiều nhất.

---

# Bình luận

Tạo model Comment:

- article
- user
- content
- created_at

Yêu cầu:

- Bình luận đơn giản
- Không cần reply
- Chỉ người dùng đăng nhập mới được bình luận

---

# Chức năng yêu thích

Tạo hệ thống Like:

Người dùng có thể:

- Thích bài viết
- Bỏ thích bài viết

Hiển thị:

- Tổng số lượt thích

---

# Chức năng lưu bài viết

Người dùng có thể:

- Lưu bài viết
- Bỏ lưu bài viết

Tạo trang:

Saved Articles

Hiển thị:

- Danh sách bài viết đã lưu

---

# Tìm kiếm

Cho phép tìm kiếm theo:

- Tiêu đề
- Nội dung
- Tags
- Tác giả

Không cần bộ lọc nâng cao.

---

# Quản trị

Sử dụng Django Admin mặc định.

Admin quản lý:

- Bài viết
- Người dùng
- Bình luận

Tùy chỉnh Django Admin để dễ quản lý.

---

# Trang cần xây dựng

1. Trang chủ

Hiển thị:

- Hero Banner
- Breaking News
- Tin nổi bật
- Tin mới nhất
- Tin xem nhiều

2. Danh sách bài viết

3. Chi tiết bài viết

4. Trang Tags

5. Trang kết quả tìm kiếm

6. Đăng nhập

7. Đăng ký

8. Hồ sơ cá nhân

9. Bài viết đã lưu

10. Giới thiệu

---

# Thành phần giao diện

## Header

- Logo
- Menu
- Thanh tìm kiếm
- Đăng nhập

## Hero Banner

Hiển thị tin nổi bật lớn nhất.

## News Card

Bao gồm:

- Ảnh
- Tiêu đề
- Mô tả ngắn
- Ngày đăng

## Sidebar

- Tin xem nhiều
- Tags phổ biến

## Footer

- Thông tin website
- Liên hệ
- Bản quyền

---

# Template cần tạo

base.html

home.html

article_list.html

article_detail.html

search_results.html

tag_articles.html

login.html

register.html

profile.html

saved_articles.html

about.html

---

# URLs

Tạo đầy đủ URL cho:

- Trang chủ
- Danh sách bài viết
- Chi tiết bài viết
- Like
- Save
- Search
- Login
- Logout
- Register
- Profile

---

# Views

Sử dụng Function Based Views.

Tạo đầy đủ:

- Home View
- Article List View
- Article Detail View
- Search View
- Like View
- Save View
- Login View
- Register View
- Profile View

---

# Kết quả mong muốn

AI phải sinh:

1. Cấu trúc thư mục dự án hoàn chỉnh.

2. Toàn bộ models.py.

3. Toàn bộ urls.py.

4. Toàn bộ views.py.

5. Toàn bộ admin.py.

6. Toàn bộ template skeleton.

7. Hướng dẫn migrate.

8. Hướng dẫn chạy dự án.

9. Giải thích luồng hoạt động của website.

10. Đề xuất các bước phát triển tiếp theo.
