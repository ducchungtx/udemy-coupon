# Udemy Coupon Finder

Ứng dụng web giúp tìm kiếm và trích xuất các khóa học miễn phí từ HacksNation.

![Udemy Coupon Finder](https://i.imgur.com/YIx5rAA.png)

## Tính năng

- Hiển thị danh sách các bài đăng coupon mới nhất từ HacksNation
- Trích xuất danh sách khóa học từ một bài đăng cụ thể
- Phân trang và sắp xếp kết quả
- Hỗ trợ cả tương tác bằng cách nhấp vào bài đăng hoặc nhập URL thủ công
- Tự động xử lý các URL và trích xuất thông tin khóa học
- Hiển thị liên kết đăng ký trực tiếp đến Udemy

## Cài đặt

### Yêu cầu

- Python 3.6+
- Flask
- Requests
- BeautifulSoup4
- Selenium (để xử lý các trang AJAX)
- ChromeDriver/WebDriver Manager

### Bước cài đặt

1. Clone repository:
```
git clone <repository-url>
cd udemy-coupon
```

2. Tạo và kích hoạt môi trường ảo (tùy chọn nhưng khuyến nghị):
```
python -m venv venv
source venv/bin/activate  # Trên macOS/Linux
# hoặc
.\venv\Scripts\activate  # Trên Windows
```

3. Cài đặt các dependencies:
```
pip install -r requirements.txt
```

4. Chạy ứng dụng:
```
python main.py
```

5. Mở trình duyệt và truy cập:
```
http://127.0.0.1:5000
```

## Cấu trúc dự án

```
udemy-coupon/
├── app.py              # File chính của ứng dụng Flask
├── main.py             # Entry point để chạy ứng dụng
├── requirements.txt    # Các dependencies
├── README.md           # Tài liệu hướng dẫn
├── scrapers/           # Module scraping
│   ├── __init__.py
│   ├── course_extractor.py  # Logic trích xuất khóa học
│   └── hacksnation.py       # Logic lấy dữ liệu từ HacksNation
├── templates/          # Templates HTML
│   └── index.html      # Trang chính của ứng dụng
└── utils/              # Các hàm tiện ích
    ├── __init__.py
    └── helpers.py      # Hàm tiện ích
```

## Hướng dẫn sử dụng

1. **Xem danh sách bài đăng coupon mới nhất**:
   - Khi ứng dụng khởi động, các bài đăng mới nhất từ HacksNation sẽ tự động được hiển thị ở phần "Latest Coupon Posts".

2. **Trích xuất khóa học từ một bài đăng**:
   - **Cách 1**: Nhấp vào bất kỳ bài đăng nào trong danh sách để tự động trích xuất các khóa học.
   - **Cách 2**: Sao chép URL của bài đăng, dán vào ô nhập liệu và nhấp vào nút "Extract Courses".

3. **Xem và quản lý danh sách khóa học**:
   - Sử dụng điều khiển phân trang để duyệt qua các trang kết quả
   - Thay đổi số lượng khóa học hiển thị mỗi trang bằng menu dropdown
   - Nhấp vào "Toggle Sort Order" để thay đổi thứ tự sắp xếp
   - Nhấp vào "Enroll for Free" để đăng ký khóa học trên Udemy

## Cách đóng góp

1. Fork repository
2. Tạo nhánh tính năng (`git checkout -b feature/amazing-feature`)
3. Commit thay đổi của bạn (`git commit -m 'Add some amazing feature'`)
4. Push lên nhánh (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## Giấy phép

Phân phối theo giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## Liên hệ

Tên của bạn - [@twitter_handle](https://twitter.com/chungng7) - ducchungtx@gmail.com

Project Link: [https://github.com/ducchungtx/udemy-coupon](https://github.com/ducchungtx/udemy-coupon)