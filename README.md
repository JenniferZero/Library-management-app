# Ứng dụng Quản lý Thư Viện

Một ứng dụng quản lý thư viện với các tính năng xác thực người dùng, quản lý sách và thu thập dữ liệu.

---

## Cài đặt

### Bước 1: Sao chép (clone) kho lưu trữ

Sao chép kho lưu trữ dự án về máy của bạn:

```sh
git clone https://github.com/JenniferZero/Library-management-app.git
cd Library-management-app
```

---

### Bước 2: Thiết lập môi trường ảo (tùy chọn)

Tạo và kích hoạt môi trường ảo để cô lập các thư viện phụ thuộc:

#### Trên Windows:
```sh
python -m venv venv
venv\Scripts\activate
```

#### Trên macOS/Linux:
```sh
python3 -m venv venv
source venv/bin/activate
```

---

### Bước 3: Cài đặt các thư viện phụ thuộc

Cài đặt tất cả các thư viện phụ thuộc từ tệp `requirements.txt`:

```sh
pip install -r requirements.txt
```

Nếu một số thư viện bị thiếu, hãy cài đặt chúng thủ công:

```sh
pip install aiohttp beautifulsoup4 customtkinter
```

---

## Chạy ứng dụng

### Bước 1: Điều hướng đến thư mục nguồn

```sh
cd src
```

### Bước 2: Chạy ứng dụng

Chạy ứng dụng bằng Python:

```sh
python library_manager.py
```

---

## Tệp dữ liệu

Ứng dụng sử dụng một số tệp JSON để lưu trữ dữ liệu. Các tệp này nằm trong thư mục `src/data`:

- `users.json`: Lưu trữ thông tin người dùng.
- `books.json`: Lưu trữ thông tin sách.
- `readers.json`: Lưu trữ thông tin độc giả.
- `borrow.json`: Lưu trữ thông tin mượn sách.

Đảm bảo các tệp này có mặt trong thư mục `src/data` trước khi chạy ứng dụng. Nếu chúng bị thiếu, hãy tạo các tệp JSON trống với cùng tên.

---

## Đóng gói ứng dụng

Để đóng gói ứng dụng thành một tệp thực thi độc lập, hãy làm theo các bước sau:

### Bước 1: Cài đặt PyInstaller

Cài đặt PyInstaller bằng pip:

```sh
pip install pyinstaller
```

### Bước 2: Đóng gói ứng dụng

Chạy lệnh sau để đóng gói ứng dụng:

```sh
pyinstaller --name LibraryManager --onefile --noconsole --clean --noconfirm `
--hidden-import=aiohttp --hidden-import=bs4 --hidden-import=tkinter `
--add-data "data;data" --add-data "assets;assets" --icon "assets/open-book.ico" `
--distpath "dist" --log-level DEBUG library_manager.py
```

Để đóng gói lại ứng dụng, hãy xóa thư mục `build` và tệp `.exe` cũ.

### Bước 3: Tìm tệp thực thi

Sau khi quá trình đóng gói hoàn tất, tệp thực thi (`LibraryManager.exe`) sẽ nằm trong thư mục `dist`.

---

## Ghi chú

- Đảm bảo rằng tất cả các tệp dữ liệu cần thiết được bao gồm trong thư mục `data` khi chạy hoặc đóng gói ứng dụng.
- Nếu gặp bất kỳ vấn đề nào trong quá trình đóng gói, hãy tham khảo tài liệu của PyInstaller hoặc kiểm tra nhật ký trên terminal để xem chi tiết lỗi.