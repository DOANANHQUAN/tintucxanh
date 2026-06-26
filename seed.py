import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
django.setup()

from django.contrib.auth.models import User
from news.models import Article
from PIL import Image, ImageDraw

def create_mock_images():
    print("Generating mock thumbnails...")
    os.makedirs('media/thumbnails', exist_ok=True)
    colors = ['#1E40AF', '#F97316', '#10B981', '#EF4444', '#8B5CF6']
    for i, color in enumerate(colors, 1):
        img = Image.new('RGB', (800, 450), color=color)
        draw = ImageDraw.Draw(img)
        # Draw some simple design on it
        draw.rectangle([50, 50, 750, 400], outline="white", width=5)
        # Save image
        img.save(f'media/thumbnails/thumb_{i}.png')

def seed_data():
    create_mock_images()
    
    # Get the admin user
    try:
        author = User.objects.get(username='admin')
    except User.DoesNotExist:
        author = User.objects.create_superuser('admin', 'admin@tintucxanh.com', 'admin')
        
    # Clear existing articles
    Article.objects.all().delete()
    
    articles_data = [
        {
            'title': 'Kỷ nguyên Trí tuệ Nhân tạo thế hệ mới (AI) thay đổi thế giới ra sao?',
            'slug': 'ky-nguyen-tri-tue-nhan-tao-the-he-moi',
            'thumbnail': 'thumbnails/thumb_1.png',
            'content': """Trí tuệ nhân tạo (AI) đang trải qua một giai đoạn phát triển thần tốc, chuyển dịch mạnh mẽ từ các thuật toán phân tích truyền thống sang các hệ thống Generative AI tiên tiến có khả năng tự sáng tạo nội dung, mã nguồn và thậm chí cả tác phẩm nghệ thuật.

Trong y tế, AI đang hỗ trợ các bác sĩ chẩn đoán hình ảnh chính xác đến 99% các khối u siêu nhỏ và giúp rút ngắn thời gian nghiên cứu vaccine từ hàng năm xuống chỉ còn vài tuần.

Trong giáo dục, mô hình trợ lý học tập cá nhân hóa sử dụng AI đang giúp mỗi học sinh tiếp thu bài học theo đúng năng lực cá nhân.

Tuy nhiên, sự phát triển này cũng đi kèm với nhiều thách thức lớn về bảo mật dữ liệu, bản quyền và đạo đức AI. Các quốc gia đang ráo riết chuẩn bị các khung pháp lý để quản lý AI một cách an toàn và bền vững.""",
            'tags': 'Công nghệ, AI, Tương lai',
            'views': 1250,
            'is_featured': True
        },
        {
            'title': 'Những xu hướng phát triển Game Việt năm 2026',
            'slug': 'nhung-xu-huong-phat-trien-game-viet-nam-2026',
            'thumbnail': 'thumbnails/thumb_2.png',
            'content': """Thị trường phát triển game tại Việt Nam đang ghi nhận những bước chuyển mình mạnh mẽ với sự trỗi dậy của các studio indie quy mô nhỏ nhưng sở hữu ý tưởng đột phá. Các thể loại game lấy chất liệu văn hóa, lịch sử dân gian Việt Nam đang nhận được sự ủng hộ nhiệt tình từ cộng đồng game thủ nội địa và quốc tế.

Nhiều chuyên gia dự báo trong năm 2026, các công nghệ như thực tế ảo tăng cường (AR/VR) kết hợp với các công cụ tối ưu hóa bằng trí tuệ nhân tạo sẽ giúp các nhà phát triển game tối giản hóa quy trình thiết kế đồ họa 3D, từ đó nâng cao chất lượng trải nghiệm của game Việt trên thị trường quốc tế.""",
            'tags': 'Game, Công nghệ, Việt Nam',
            'views': 890,
            'is_featured': True
        },
        {
            'title': 'Cải cách giáo dục thời đại số: Học sinh tự học làm trung tâm',
            'slug': 'cai-cach-giao-duc-thoi-dai-so-hoc-sinh-tu-hoc-lam-trung-tam',
            'thumbnail': 'thumbnails/thumb_3.png',
            'content': """Phương pháp giáo dục truyền thống nơi giáo viên giảng bài và học sinh ghi chép đang dần được thay thế bằng mô hình lớp học đảo ngược (Flipped Classroom) và giáo trình trực tuyến tương tác cao. Học sinh được khuyến khích tự tìm tòi, thực hiện các dự án nghiên cứu nhỏ thông qua các tài nguyên số trước khi đến lớp thảo luận.

Sự chuyển dịch này không chỉ giúp phát triển kỹ năng tư duy phản biện độc lập mà còn chuẩn bị cho người học khả năng tự thích ứng với sự thay đổi liên tục của thị trường lao động tương lai.""",
            'tags': 'Giáo dục, Công nghệ, Học tập',
            'views': 450,
            'is_featured': False
        },
        {
            'title': 'Giải đấu Thể thao Điện tử Sinh viên toàn quốc chuẩn bị khởi tranh',
            'slug': 'giai-dau-the-thao-dien-tu-sinh-vien-toan-quoc',
            'thumbnail': 'thumbnails/thumb_4.png',
            'content': """Với sự tham gia của hơn 100 trường đại học và cao đẳng trên toàn quốc, giải đấu Esports sinh viên năm nay hứa hẹn sẽ mang đến những màn so tài mãn nhãn ở các bộ môn thi đấu phổ biến. Ban tổ chức cho biết giải đấu nhằm mục tiêu thúc đẩy phong trào thể thao điện tử lành mạnh, xây dựng tính kỷ luật, tinh thần đồng đội và tìm kiếm các nhân tài trẻ tuổi đại diện quốc gia đi thi đấu khu vực.""",
            'tags': 'Thể thao, Game, Sinh viên',
            'views': 620,
            'is_featured': False
        },
        {
            'title': 'Cách bảo vệ sức khỏe khi làm việc liên tục trước máy tính',
            'slug': 'cach-bao-ve-suc-khoe-khi-lam-viec-truoc-may-tinh',
            'thumbnail': 'thumbnails/thumb_5.png',
            'content': """Làm việc liên tục trước màn hình máy tính gây ra nhiều vấn đề như mỏi mắt, đau cổ vai gáy và suy giảm thể lực. Các bác sĩ khuyên áp dụng quy tắc 20-20-20 (mỗi 20 phút nhìn xa 20 feet trong 20 giây), điều chỉnh độ cao ghế ngồi phù hợp và thực hiện các động tác căng cơ nhẹ nhàng tại chỗ để bảo vệ sức khỏe lâu dài.""",
            'tags': 'Sức khỏe, Đời sống, Công sở',
            'views': 1500,
            'is_featured': True
        }
    ]
    
    for item in articles_data:
        Article.objects.create(
            title=item['title'],
            slug=item['slug'],
            thumbnail=item['thumbnail'],
            content=item['content'],
            author=author,
            tags=item['tags'],
            views=item['views'],
            is_featured=item['is_featured']
        )
    print("Seed data completed successfully!")

if __name__ == '__main__':
    seed_data()
