import tkinter as tk
import threading
import json
import os
import asyncio
import aiohttp
import customtkinter as ctk

from PIL import Image, ImageTk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from bs4 import BeautifulSoup
from customtkinter import CTkButton, CTkEntry, CTkLabel, CTkFrame, CTkImage, CTkScrollbar, CTkToplevel, CTkRadioButton, CTkCheckBox

# Thiết lập theme và mode cho CustomTkinter
ctk.set_appearance_mode("Light")  # Modes: "System", "Dark", "Light" \ Thay đổi giá trị này để thay đổi chế độ giao diện
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


if __name__ == "__main__" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Định nghĩa thư mục chứa dữ liệu JSON
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Đường dẫn tới các file JSON
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.json')
READERS_FILE = os.path.join(DATA_DIR, 'readers.json')
BORROW_FILE = os.path.join(DATA_DIR, 'borrow.json')

# Biến theo dõi trạng thái thu gọn của các khung
is_books_collapsed = False
is_readers_collapsed = False
is_borrow_collapsed = False

# Hàm đọc dữ liệu từ file JSON
def read_json(file_path):
    if not os.path.exists(file_path):  
        print(f"File {file_path} không tồn tại.")
        return []  
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            if not content.strip(): 
                print(f"File {file_path} rỗng.")
                return []
            return json.loads(content) 
    except json.JSONDecodeError as e:
        print(f"Lỗi khi đọc JSON: {e}")
        return []  


def write_json(file_path, data):
    if not data:  # Nếu dữ liệu rỗng, không ghi vào file
        print("Cảnh báo: Không ghi dữ liệu rỗng vào file JSON!")
        return

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Hàm đọc danh sách URL từ file
def read_urls_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    return []


# Hàm crawl dữ liệu sách từ Open Library
async def crawl_data(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            title = soup.find('h1').text.strip() if soup.find('h1') else "-"
            author = soup.find('a', {'itemprop': 'author'}).text.strip() if soup.find('a', {'itemprop': 'author'}) else "-"
            publish_date = soup.find('span', {'itemprop': 'datePublished'})
            year = publish_date.text.strip() if publish_date else "-"
            
            pages_element = soup.find('span', {'itemprop': 'numberOfPages'})
            pages = pages_element.text.strip() if pages_element else "0"
            
            return {
                "id": url.split('/')[-1],
                "title": title,
                "author": author,
                "year": year,
                "pages": int(pages) if pages.isdigit() else 0 
            }
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return None

# Hàm crawl dữ liệu sách với set requests 
async def crawl_books(book_urls, max_concurrent_requests=3):
    connector = aiohttp.TCPConnector(limit_per_host=max_concurrent_requests)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [crawl_data(session, url) for url in book_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if result is not None and not isinstance(result, Exception)]

# Hàm crawl data bất đồng bộ được chạy trong một thread riêng
def async_crawl_books_with_progress():
    book_urls_file = os.path.join(DATA_DIR, 'book_urls.txt')
    book_urls = read_urls_from_file(book_urls_file)
    
    # Hiển thị thanh tiến trình
    progress_window = tk.Toplevel()
    progress_window.title("Đang Crawl Dữ Liệu")
    progress_window.geometry("400x100")
    
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "open-book.ico")
    progress_window.iconbitmap(logo_path)
    
    tk.Label(progress_window, text="Đang crawl dữ liệu, vui lòng chờ...").pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress_bar.pack(pady=10)
    
    def crawl_with_progress():
        total_urls = len(book_urls)
        progress_bar["maximum"] = total_urls
        
        async def crawl_and_update():
            connector = aiohttp.TCPConnector(limit_per_host=3)
            async with aiohttp.ClientSession(connector=connector) as session:
                for i, url in enumerate(book_urls, start=1):
                    result = await crawl_data(session, url)
                    if result:
                        books_data.append(result)
                    
                    # Cập nhật progress_bar trong luồng chính
                    progress_window.after(0, progress_bar.config, {"value": i})
                    progress_window.update_idletasks()
        
        books_data = []
        asyncio.run(crawl_and_update())
        write_json(BOOKS_FILE, books_data)
        progress_window.destroy()
        messagebox.showinfo("Thành công", "Tiến trình crawl hoàn tất! Dữ liệu đã được cập nhật.")
    
    threading.Thread(target=crawl_with_progress).start()

# Cập nhật hàm khởi chạy crawl data trong thread riêng
def threaded_crawl_data():
    t = threading.Thread(target=async_crawl_books_with_progress)
    t.start()

# Hàm tạo cửa sổ đăng nhập
def create_login_window():
    global login_window, entry_username, entry_password
    root.withdraw()  # Ẩn cửa sổ chính
    
    login_window = CTkToplevel()
    login_window.title("Đăng Nhập")
    login_window.geometry("2000x1200")
    login_window.after(200, lambda: login_window.iconbitmap(logo_path))
    
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "open-book.ico")
    
    # Tạo một frame chính để chứa toàn bộ nội dung
    main_frame = CTkFrame(login_window, corner_radius=0, fg_color="transparent")
    main_frame.pack(fill="both", expand=True)

    # Thêm hình ảnh vào trang đăng nhập - phủ toàn màn hình
    image_path = os.path.join(os.path.dirname(__file__), "assets", "library.png")
    img = Image.open(image_path)
    img = img.resize((1800, 900), Image.Resampling.LANCZOS)
    ct_img = CTkImage(light_image=img, dark_image=img, size=(1800, 900))
    
    # Tạo label chứa hình nền
    bg_label = CTkLabel(main_frame, image=ct_img, text="")
    bg_label.place(relx=0.5, rely=0.5, anchor="center")
    
    # Frame đăng nhập nổi trên hình nền 
    frame = CTkFrame(main_frame, corner_radius=15, fg_color=("white", "#212121"), border_width=2, border_color=("gray75", "gray25"))
    frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.25, relheight=0.65)
    
    CTkLabel(frame, text="ĐĂNG NHẬP", font=("Arial", 24, "bold")).pack(pady=(40, 20))
    
    # Form đăng nhập
    form_frame = CTkFrame(frame, fg_color="transparent")
    form_frame.pack(pady=10, padx=30, fill="both", expand=False)
    
    CTkLabel(form_frame, text="Tài khoản", font=("Arial", 14), anchor="w").pack(pady=3, anchor="w")
    entry_username = CTkEntry(form_frame, font=("Arial", 14), width=50, height=40, placeholder_text="Nhập tên đăng nhập")
    entry_username.pack(pady=(0, 15), fill="x")
    
    CTkLabel(form_frame, text="Mật khẩu", font=("Arial", 14), anchor="w").pack(pady=3, anchor="w")
    entry_password = CTkEntry(form_frame, show="•", font=("Arial", 14), width=50, height=40, placeholder_text="Nhập mật khẩu")
    entry_password.pack(pady=(0, 5), fill="x")
    
    # Biến để theo dõi trạng thái hiển thị mật khẩu
    password_visible = False
    
    # Hàm chuyển đổi hiển thị mật khẩu
    def toggle_password_visibility():
        nonlocal password_visible
        password_visible = not password_visible
        entry_password.configure(show="" if password_visible else "•")
    
    # Checkbox hiển thị mật khẩu
    pw_visibility_frame = CTkFrame(form_frame, fg_color="transparent")
    pw_visibility_frame.pack(pady=5, fill="x", anchor="w")
    
    pw_visibility_checkbox = CTkCheckBox(pw_visibility_frame, text="Hiển thị mật khẩu", command=toggle_password_visibility)
    pw_visibility_checkbox.pack(side="left", anchor="w")
    
    # Thêm chức năng nhớ đăng nhập (giả lập)
    remember_frame = CTkFrame(form_frame, fg_color="transparent")
    remember_frame.pack(pady=10, fill="x")
    
    remember_var = ctk.IntVar(value=0)
    remember_check = ctk.CTkCheckBox(remember_frame, text="Nhớ tài khoản", variable=remember_var, onvalue=1, offvalue=0)
    remember_check.pack(side="left", anchor="w")
    
    # Nút đăng nhập
    login_button = CTkButton(form_frame, text="Đăng nhập", command=login, font=("Arial", 14), width=200, height=45, 
                           fg_color=("#3a7ebf", "#1f538d"), hover_color=("#325882", "#14375e"))
    login_button.pack(pady=(20, 10))
    
    CTkLabel(form_frame, text="Chưa có tài khoản?", font=("Arial", 12)).pack(pady=(10, 5))
    
    # Nút đăng ký
    register_button = CTkButton(form_frame, text="Đăng ký", command=create_register_window, font=("Arial", 14), width=200, height=45,
                              fg_color=("#28a745", "#218838"), hover_color=("#218838", "#1e7e34"))
    register_button.pack(pady=(5, 20))

# Hàm tạo cửa sổ đăng ký
def create_register_window():
    global register_window, entry_new_username, entry_new_password
    register_window = CTkToplevel()
    register_window.title("Đăng Ký")
    register_window.geometry("450x520")
    register_window.after(200, lambda: register_window.iconbitmap(logo_path))
    
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "open-book.ico")
    
    # Tạo khung chính
    main_frame = CTkFrame(register_window)
    main_frame.pack(pady=20, padx=40, fill="both", expand=True)
    
    CTkLabel(main_frame, text="ĐĂNG KÝ TÀI KHOẢN", font=("Arial", 20, "bold")).pack(pady=20)
    
    # Form đăng ký
    form_frame = CTkFrame(main_frame)
    form_frame.pack(pady=15, padx=20, fill="both", expand=True)
    
    CTkLabel(form_frame, text="Tên đăng nhập mới:", font=("Arial", 14), anchor="w").pack(padx=20, pady=1, anchor="w")
    entry_new_username = CTkEntry(form_frame, font=("Arial", 14), width=300, height=40, 
                                 placeholder_text="Nhập tên đăng nhập")
    entry_new_username.pack(pady=10)
    
    CTkLabel(form_frame, text="Mật khẩu mới:", font=("Arial", 14), anchor="w").pack(padx=20, pady=1, anchor="w")
    entry_new_password = CTkEntry(form_frame, show="•", font=("Arial", 14), width=300, height=40,
                                 placeholder_text="Nhập mật khẩu")
    entry_new_password.pack(pady=10)
    
    # Thêm trường xác nhận mật khẩu (chỉ cho UI, không xử lý logic)
    CTkLabel(form_frame, text="Xác nhận mật khẩu:", font=("Arial", 14), anchor="w").pack(padx=20, pady=1, anchor="w")
    confirm_password = CTkEntry(form_frame, show="•", font=("Arial", 14), width=300, height=40,
                               placeholder_text="Nhập lại mật khẩu")
    confirm_password.pack(pady=10)
    
    # Nút đăng ký và hủy
    button_frame = CTkFrame(form_frame, fg_color="transparent")
    button_frame.pack(pady=20)
    
    CTkButton(button_frame, text="Đăng ký", command=register, font=("Arial", 14), width=120, height=40,
             fg_color=("#28a745", "#218838"), hover_color=("#218838", "#1e7e34")).pack(side="left", padx=10)
    
    CTkButton(button_frame, text="Hủy", command=register_window.destroy, font=("Arial", 14), width=120, height=40,
             fg_color=("#dc3545", "#c82333"), hover_color=("#c82333", "#bd2130")).pack(side="right", padx=10)

# Hàm đăng ký tài khoản mới
def register():
    new_username = entry_new_username.get()
    new_password = entry_new_password.get()
    
    if not new_username or not new_password:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
        return
    
    users = read_json(USERS_FILE)
    for user in users:
        if user["username"] == new_username:
            messagebox.showerror("Lỗi", "Tài khoản đã tồn tại.")
            return 
    
    new_user = {"username": new_username, "password": new_password, "role": "user"}
    users.append(new_user)
    write_json(USERS_FILE, users)
    messagebox.showinfo("Thành công", "Đăng ký tài khoản thành công.")
    register_window.destroy()

# Hàm đăng nhập
def login():
    username = entry_username.get()
    password = entry_password.get()
    
    users = read_json(USERS_FILE)
    for user in users:
        if user["username"] == username and user["password"] == password:
            global current_user
            current_user = user
            messagebox.showinfo("Thành công", f"Đăng nhập thành công với quyền {user['role']}.")
            login_window.destroy()
            root.deiconify()
            if user["role"] == "admin":
                enable_admin_features()
            else:
                disable_admin_features()
            return
    
    messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng.")
    
# Hàm tạo cửa sổ thông báo với logo tùy chỉnh 
def custom_messagebox(title, message, icon="info"):
    msg_window = tk.Toplevel()
    msg_window.title(title)
    msg_window.geometry("350x150")
    msg_window.resizable(False, False)
    
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "open-book.ico")
    msg_window.iconbitmap(logo_path)
    
    tk.Label(msg_window, text=message, font=("Arial", 24), wraplength=300).pack(pady=20)
    
    # Thêm biểu tượng tùy thuộc vào loại thông báo
    if icon == "info":
        icon_label = tk.Label(msg_window, text="ℹ️", font=("Arial", 24))
    elif icon == "warning":
        icon_label = tk.Label(msg_window, text="⚠️", font=("Arial", 24))
    elif icon == "error":
        icon_label = tk.Label(msg_window, text="❌", font=("Arial", 24))
    else:
        icon_label = tk.Label(msg_window, text="", font=("Arial", 24))
    icon_label.pack(pady=5)
    
    tk.Button(msg_window, text="OK", command=msg_window.destroy).pack(pady=10)
    
    # Đặt cửa sổ ở giữa màn hình
    msg_window.transient(root)
    msg_window.grab_set()
    root.wait_window(msg_window)

# Hàm kích hoạt các tính năng của admin
def enable_admin_features():
    add_book.configure(state="normal")
    delete_book.configure(state="normal")
    edit_book.configure(state="normal")
    add_reader.configure(state="normal")
    delete_reader.configure(state="normal")
    edit_reader.configure(state="normal")
    delete_borrow.configure(state="normal")
    edit_borrow.configure(state="normal")
    crawl_button.configure(state="normal")

# Hàm vô hiệu hóa các tính năng của admin cho user thường
def disable_admin_features():
    add_book.configure(state="disabled")
    delete_book.configure(state="disabled")
    edit_book.configure(state="disabled")
    add_reader.configure(state="disabled")
    delete_reader.configure(state="disabled")
    edit_reader.configure(state="disabled")
    delete_borrow.configure(state="disabled")
    edit_borrow.configure(state="disabled")
    crawl_button.configure(state="disabled")

# Hàm kiểm tra quyền truy cập
def parse_ids(id_input):
    id_input = id_input.strip()
    try:
        return [x.strip() for x in id_input.split(',')]
    except ValueError:
        return None

# Hàm tạo cửa sổ hồ sơ người dùng
def create_profile_window():
    global profile_window
    profile_window = CTkToplevel()
    profile_window.title("Hồ Sơ Người Dùng")
    profile_window.geometry("400x550")
    profile_window.after(200, lambda: profile_window.iconbitmap(logo_path))
    
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "open-book.ico")
    
    # Tạo frame chính
    main_frame = CTkFrame(profile_window)
    main_frame.pack(pady=20, padx=40, fill="both", expand=True)
    
    CTkLabel(main_frame, text="HỒ SƠ NGƯỜI DÙNG", font=("Arial", 20, "bold")).pack(pady=20)
    
    # Hiển thị avatar (giả lập)
    avatar_frame = CTkFrame(main_frame, width=150, height=150, corner_radius=75)
    avatar_frame.pack(pady=10)
    CTkLabel(avatar_frame, text="👤", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")
    
    # Thông tin người dùng
    info_frame = CTkFrame(main_frame)
    info_frame.pack(pady=15, padx=20, fill="both", expand=True)
    
    # Tạo frame cho thông tin tài khoản
    account_frame = CTkFrame(info_frame, fg_color="transparent")
    account_frame.pack(anchor="w", pady=5, fill="x")
    CTkLabel(account_frame, text=f"Tài khoản:", font=("Arial", 14, "bold"), width=100).pack(side="left", padx=(0, 10))
    CTkLabel(account_frame, text=f"{current_user['username']}", font=("Arial", 16)).pack(side="left")

    # Tạo frame cho thông tin quyền
    role_frame = CTkFrame(info_frame, fg_color="transparent")
    role_frame.pack(anchor="w", pady=5, fill="x")
    CTkLabel(role_frame, text=f"Quyền:", font=("Arial", 14, "bold"), width=100).pack(side="left", padx=(0, 10))
    CTkLabel(role_frame, text=f"{current_user['role']}", font=("Arial", 16)).pack(side="left")
    
    # Điều chỉnh giao diện
    appearance_frame = CTkFrame(main_frame)
    appearance_frame.pack(pady=10, padx=20, fill="x")
    
    CTkLabel(appearance_frame, text="Chế độ giao diện:", font=("Arial", 14, "bold")).pack(anchor="w",padx= 10, pady=5)
    
    def change_appearance_mode(new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
    
    appearance_option = ctk.StringVar(value=ctk.get_appearance_mode())
    light_radio = CTkRadioButton(appearance_frame, text="Sáng", variable=appearance_option, value="Light", 
                               command=lambda: change_appearance_mode("Light"))
    light_radio.pack(side="left", padx=20)
    
    dark_radio = CTkRadioButton(appearance_frame, text="Tối", variable=appearance_option, value="Dark", 
                              command=lambda: change_appearance_mode("Dark"))
    dark_radio.pack(side="left", padx=20)
    
    system_radio = CTkRadioButton(appearance_frame, text="Hệ thống", variable=appearance_option, value="System", 
                                command=lambda: change_appearance_mode("System"))
    system_radio.pack(side="left", padx=20)
    
    # Nút đăng xuất
    CTkButton(main_frame, text="Đăng Xuất", command=logout, font=("Arial", 14), 
             fg_color=("#dc3545", "#c82333"), hover_color=("#c82333", "#bd2130"),
             width=120, height=40).pack(pady=20)

# Hàm đăng xuất
def logout():
    global current_user
    current_user = None
    profile_window.destroy()
    root.withdraw()
    create_login_window()

# Hàm kiểm tra định dạng ngày
def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Hàm kiểm tra định dạng số nguyên
def validate_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

# Hàm thêm sách mới
def add_book():
    book_id = entry_id.get()
    title = entry_title.get()
    author = entry_author.get()
    year = entry_year.get()
    pages = entry_pages.get()

    if not title or not author or not year or not pages:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sách.")
        return

    if not validate_int(year):
        messagebox.showerror("Lỗi", "Năm xuất bản phải là số nguyên.")
        return

    if not validate_int(pages):
        messagebox.showerror("Lỗi", "Số trang phải là số nguyên.")
        return
    
    books = read_json(BOOKS_FILE)
    new_book = {
        "id": book_id,
        "title": title,
        "author": author,
        "year": int(year),
        "pages": int(pages)
    }
    books.append(new_book)
    write_json(BOOKS_FILE, books)
    messagebox.showinfo("Thành công", "Thêm sách mới thành công.")
    clear_entries()
    
# Hàm thêm độc giả mới
def add_reader():
    reader_id = entry_reader_id.get()
    name = entry_name.get()
    address = entry_address.get()
    phone = entry_phone.get()
    email = entry_email.get()

    if not name or not address or not phone or not email:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin độc giả.")
        return

    readers = read_json(READERS_FILE)
    new_reader = {
        "id": reader_id,
        "name": name,
        "address": address,
        "phone": phone,
        "email": email
    }
    readers.append(new_reader)
    write_json(READERS_FILE, readers)
    messagebox.showinfo("Thành công", "Thêm độc giả mới thành công.")
    clear_entries()
        
# Hàm mượn sách
def borrow_book():
    reader_id = entry_borrow_reader_id.get()
    book_id = entry_borrow_book_id.get()
    borrow_date = entry_borrow_date.get()
    return_date = entry_return_date.get()

    if not reader_id or not book_id or not borrow_date or not return_date:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin mượn sách.")
        return

    if not validate_date(borrow_date):
        messagebox.showerror("Lỗi", "Ngày mượn không đúng định dạng YYYY-MM-DD.")
        return

    if not validate_date(return_date):
        messagebox.showerror("Lỗi", "Ngày trả không đúng định dạng YYYY-MM-DD.")
        return

    borrow_list = read_json(BORROW_FILE)
    new_borrow = {
        "reader_id": reader_id,
        "book_id": book_id,
        "borrow_date": borrow_date,
        "return_date": return_date
    }
    borrow_list.append(new_borrow)
    write_json(BORROW_FILE, borrow_list)
    messagebox.showinfo("Thành công", "Đăng ký mượn sách thành công.")
    clear_entries() 

# Hàm xóa sách 
def delete_book():
    id_input = entry_id.get()
    if not id_input:
        messagebox.showerror("Lỗi", "Vui lòng nhập ID sách cần xóa.")
        return

    books = read_json(BOOKS_FILE)
    initial_count = len(books)
    books = [book for book in books if book['id'] not in (id_input)]
    
    if len(books) == initial_count:
        messagebox.showerror("Lỗi", "Không tìm thấy thông tin sách với ID đã nhập.")
        return
    
    write_json(BOOKS_FILE, books)
    messagebox.showinfo("Thành công", "Xóa sách thành công.")
    clear_entries()

# Hàm xóa độc giả 
def delete_reader():
    id_input = entry_reader_id.get()
    if not id_input:
        messagebox.showerror("Lỗi", "Vui lòng nhập ID độc giả cần xóa.")
        return

    readers = read_json(READERS_FILE)
    initial_count = len(readers)
    readers = [reader for reader in readers if reader['id'] not in (id_input)]
    
    if len(readers) == initial_count:
        messagebox.showerror("Lỗi", "Không tìm thấy thông tin độc giả với ID đã nhập.")
        return
     
    write_json(READERS_FILE, readers)
    messagebox.showinfo("Thành công", "Xóa độc giả thành công.")
    clear_entries()

# Hàm xóa thông tin mượn sách
def delete_borrow():
    reader_id_input = entry_borrow_reader_id.get().strip()
    book_id_input = entry_borrow_book_id.get().strip()
    
    if not reader_id_input and not book_id_input:
        messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất ID độc giả hoặc ID sách cần xóa.")
        return

    reader_ids = parse_ids(reader_id_input) if reader_id_input else None
    if reader_id_input and reader_ids is None:
        messagebox.showerror("Lỗi", "ID độc giả phải là số nguyên hợp lệ, cách nhau bởi dấu cách nếu nhập nhiều.")
        return

    book_ids = parse_ids(book_id_input) if book_id_input else None
    if book_id_input and book_ids is None:
        messagebox.showerror("Lỗi", "ID sách phải là số nguyên hợp lệ, cách nhau bởi dấu cách nếu nhập nhiều.")
        return

    borrows = read_json(BORROW_FILE)
    initial_count = len(borrows)
    new_borrows = []
    for borrow in borrows:
        # Nếu cả 2 trường được nhập: xóa bản ghi nếu cả reader_id và book_id thỏa mãn
        if reader_ids is not None and book_ids is not None:
            if borrow["reader_id"] in reader_ids and borrow["book_id"] in book_ids:
                continue
        # Nếu chỉ nhập reader_ids: xóa các bản ghi có reader_id phù hợp
        elif reader_ids is not None:
            if borrow["reader_id"] in reader_ids:
                continue
        # Nếu chỉ nhập book_ids: xóa các bản ghi có book_id phù hợp
        elif book_ids is not None:
            if borrow["book_id"] in book_ids:
                continue
        new_borrows.append(borrow)
    
    if len(new_borrows) == initial_count:
        messagebox.showerror("Lỗi", "Không tìm thấy thông tin mượn sách với ID đã nhập.")
        return
    
    write_json(BORROW_FILE, new_borrows)
    messagebox.showinfo("Thành công", "Xóa thông tin mượn sách thành công.")
    clear_entries()

# Hàm xóa thông tin nhập liệu
def clear_entries():
    entry_id.delete(0, tk.END)
    entry_title.delete(0, tk.END)
    entry_author.delete(0, tk.END)
    entry_year.delete(0, tk.END)
    entry_pages.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_reader_id.delete(0, tk.END)
    entry_borrow_reader_id.delete(0, tk.END)
    entry_borrow_book_id.delete(0, tk.END)
    entry_borrow_date.delete(0, tk.END)
    entry_return_date.delete(0, tk.END)

# Hàm chỉnh sửa thông tin sách
def edit_book():
    book_id = entry_id.get()
    title = entry_title.get()
    author = entry_author.get()
    year = entry_year.get()
    pages = entry_pages.get()

    if not book_id or not title or not author or not year or not pages:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sách.")
        return

    books = read_json(BOOKS_FILE)
    for book in books:
        if book["id"] == book_id:
            book["title"] = title
            book["author"] = author
            book["year"] = int(year)
            book["pages"] = int(pages)
            break
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy sách với ID đã nhập.")
        return

    write_json(BOOKS_FILE, books)
    messagebox.showinfo("Thành công", "Chỉnh sửa thông tin sách thành công.")
    clear_entries()

# Hàm chỉnh sửa thông tin độc giả
def edit_reader():
    reader_id = entry_reader_id.get()
    name = entry_name.get()
    address = entry_address.get()
    phone = entry_phone.get()
    email = entry_email.get()

    if not reader_id or not name or not address or not phone or not email:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin độc giả.")
        return

    readers = read_json(READERS_FILE)
    for reader in readers:
        if reader["id"] == reader_id:
            reader["name"] = name
            reader["address"] = address
            reader["phone"] = phone
            reader["email"] = email
            break
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy độc giả với ID đã nhập.")
        return

    write_json(READERS_FILE, readers)
    messagebox.showinfo("Thành công", "Chỉnh sửa thông tin độc giả thành công.")
    clear_entries()
    
# Hàm chỉnh sửa thông tin mượn sách
def edit_borrow():
    reader_id = entry_borrow_reader_id.get()
    book_id = entry_borrow_book_id.get()
    borrow_date = entry_borrow_date.get()
    return_date = entry_return_date.get()

    if not reader_id or not book_id or not borrow_date or not return_date:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin mượn trả.")
        return

    borrows = read_json(BORROW_FILE)
    for borrow in borrows:
        if borrow["reader_id"] == int(reader_id) and borrow["book_id"] == int(book_id):
            borrow["borrow_date"] = borrow_date
            borrow["return_date"] = return_date
            break
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy thông tin mượn trả với ID đã nhập.")
        return

    write_json(BORROW_FILE, borrows)
    messagebox.showinfo("Thành công", "Chỉnh sửa thông tin mượn trả thành công.")
    clear_entries()

# Hàm hiển thị thông tin sách
def show_books():
    books = read_json(BOOKS_FILE)
    clear_entries()
    clear_display()
    
    tree["columns"] = ("STT", "ID", "Tên Sách", "Tác Giả", "Năm", "Số Trang")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("STT", anchor=tk.CENTER, width=40)
    tree.column("ID", anchor=tk.W, width=80)
    tree.column("Tên Sách", anchor=tk.W, width=300)
    tree.column("Tác Giả", anchor=tk.W, width=200)
    tree.column("Năm", anchor=tk.CENTER, width=60)
    tree.column("Số Trang", anchor=tk.CENTER, width=60)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("STT", text="STT", anchor=tk.CENTER)
    tree.heading("ID", text="ID", anchor=tk.W)
    tree.heading("Tên Sách", text="Tên Sách", anchor=tk.W)
    tree.heading("Tác Giả", text="Tác Giả", anchor=tk.W)
    tree.heading("Năm", text="Năm", anchor=tk.CENTER)
    tree.heading("Số Trang", text="Số Trang", anchor=tk.CENTER)

    for idx, book in enumerate(books, start=1):
        tree.insert("", tk.END, values=(idx, book["id"], book["title"], book["author"], book["year"], book["pages"]))


# Hàm hiển thị thông tin độc giả
def show_readers():
    readers = read_json(READERS_FILE)
    clear_entries()
    clear_display()

    tree["columns"] = ("STT", "ID", "Tên", "Địa Chỉ", "SĐT", "Email")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("STT", anchor=tk.W, width=30)
    tree.column("ID", anchor=tk.W, width=50)
    tree.column("Tên", anchor=tk.W, width=200)
    tree.column("Địa Chỉ", anchor=tk.W, width=150)
    tree.column("SĐT", anchor=tk.CENTER, width=100)
    tree.column("Email", anchor=tk.W, width=200)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("STT", text="STT", anchor=tk.W)
    tree.heading("ID", text="ID", anchor=tk.W)
    tree.heading("Tên", text="Tên", anchor=tk.W)
    tree.heading("Địa Chỉ", text="Địa Chỉ", anchor=tk.W)
    tree.heading("SĐT", text="SĐT", anchor=tk.CENTER)
    tree.heading("Email", text="Email", anchor=tk.W)

    for idx, reader in enumerate(readers, start=1):
        tree.insert("", tk.END, values=(idx, reader["id"], reader["name"], reader["address"], 
                                         reader["phone"], reader["email"]))

# Hàm hiển thị thông tin mượn sách
def show_borrows():
    borrows = read_json(BORROW_FILE)
    clear_entries()
    clear_display()

    tree["columns"] = ("STT", "ID Độc Giả", "ID Sách", "Ngày Mượn", "Ngày Trả")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("STT", anchor=tk.W, width=10)
    tree.column("ID Độc Giả", anchor=tk.W, width=100)
    tree.column("ID Sách", anchor=tk.W, width=500)
    tree.column("Ngày Mượn", anchor=tk.CENTER, width=120)
    tree.column("Ngày Trả", anchor=tk.CENTER, width=120)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("STT", text="STT", anchor=tk.W)
    tree.heading("ID Độc Giả", text="ID Độc Giả", anchor=tk.W)
    tree.heading("ID Sách", text="ID Sách", anchor=tk.W)
    tree.heading("Ngày Mượn", text="Ngày Mượn", anchor=tk.CENTER)
    tree.heading("Ngày Trả", text="Ngày Trả", anchor=tk.CENTER)

    for idx, borrow in enumerate(borrows, start=1):
        tree.insert("", tk.END, values=(idx, borrow["reader_id"], borrow["book_id"], 
                                         borrow["borrow_date"], borrow["return_date"]))

# Hàm tìm kiếm thông tin
def search_info():
    search_type = search_combobox.get()
    keyword = search_entry.get().strip().lower()

    if not keyword:
        messagebox.showerror("Lỗi", "Vui lòng nhập từ khóa tìm kiếm.")
        return

    # Lấy dữ liệu từ file JSON tương ứng
    if search_type == "Sách":
        items = read_json(BOOKS_FILE)
    elif search_type == "Độc Giả":
        items = read_json(READERS_FILE)
    elif search_type == "Mượn Trả":
        items = read_json(BORROW_FILE)
    else:
        messagebox.showerror("Lỗi", "Vui lòng chọn loại thông tin cần tìm kiếm.")
        return

    # Tìm kiếm từ khóa trong tất cả các trường của từng mục
    results = []
    for item in items:
        for value in item.values():
            if keyword in str(value).lower():
                results.append(item)
                break

    # Hiển thị kết quả tìm kiếm
    clear_display()
    if search_type == "Sách":
        tree["columns"] = ("STT", "ID", "Tên Sách", "Tác Giả", "Năm", "Số Trang")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("STT", anchor=tk.CENTER, width=40)
        tree.column("ID", anchor=tk.W, width=80)
        tree.column("Tên Sách", anchor=tk.W, width=300)
        tree.column("Tác Giả", anchor=tk.W, width=200)
        tree.column("Năm", anchor=tk.CENTER, width=60)
        tree.column("Số Trang", anchor=tk.CENTER, width=60)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("STT", text="STT", anchor=tk.CENTER)
        tree.heading("ID", text="ID", anchor=tk.W)
        tree.heading("Tên Sách", text="Tên Sách", anchor=tk.W)
        tree.heading("Tác Giả", text="Tác Giả", anchor=tk.W)
        tree.heading("Năm", text="Năm", anchor=tk.CENTER)
        tree.heading("Số Trang", text="Số Trang", anchor=tk.CENTER)

        for idx, item in enumerate(results, start=1):
            tree.insert("", tk.END, values=(idx, item["id"], item["title"], item["author"], item["year"], item["pages"]))
    elif search_type == "Độc Giả":
        tree["columns"] = ("STT", "ID", "Tên", "Địa Chỉ", "SĐT", "Email")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("STT", anchor=tk.W, width=30)
        tree.column("ID", anchor=tk.W, width=50)
        tree.column("Tên", anchor=tk.W, width=200)
        tree.column("Địa Chỉ", anchor=tk.W, width=150)
        tree.column("SĐT", anchor=tk.CENTER, width=100)
        tree.column("Email", anchor=tk.W, width=200)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("STT", text="STT", anchor=tk.W)
        tree.heading("ID", text="ID", anchor=tk.W)
        tree.heading("Tên", text="Tên", anchor=tk.W)
        tree.heading("Địa Chỉ", text="Địa Chỉ", anchor=tk.W)
        tree.heading("SĐT", text="SĐT", anchor=tk.CENTER)
        tree.heading("Email", text="Email", anchor=tk.W)

        for idx, item in enumerate(results, start=1):
            tree.insert("", tk.END, values=(idx, item["id"], item["name"], item["address"], item["phone"], item["email"]))
    elif search_type == "Mượn Trả":
        tree["columns"] = ("STT", "ID Độc Giả", "ID Sách", "Ngày Mượn", "Ngày Trả")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("STT", anchor=tk.W, width=10)
        tree.column("ID Độc Giả", anchor=tk.W, width=100)
        tree.column("ID Sách", anchor=tk.W, width=500)
        tree.column("Ngày Mượn", anchor=tk.CENTER, width=120)
        tree.column("Ngày Trả", anchor=tk.CENTER, width=120)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("STT", text="STT", anchor=tk.W)
        tree.heading("ID Độc Giả", text="ID Độc Giả", anchor=tk.W)
        tree.heading("ID Sách", text="ID Sách", anchor=tk.W)
        tree.heading("Ngày Mượn", text="Ngày Mượn", anchor=tk.CENTER)
        tree.heading("Ngày Trả", text="Ngày Trả", anchor=tk.CENTER)

        for idx, item in enumerate(results, start=1):
            tree.insert("", tk.END, values=(idx, item["reader_id"], item["book_id"], item["borrow_date"], item["return_date"]))

    if not results:
        messagebox.showinfo("Kết Quả", "Không tìm thấy kết quả phù hợp.")
# Hàm xóa thông tin hiển thị
def clear_display():
    # Xóa tất cả các mục trong Treeview
    for item in tree.get_children():
        tree.delete(item)
    
    # Xóa cấu trúc cột hiện tại
    tree["columns"] = ()
    tree.delete(*tree.get_children())

# Hàm thu gọn/mở rộng khung quản lý sách
def toggle_books_frame():
    global is_books_collapsed
    is_books_collapsed = not is_books_collapsed
    
    if is_books_collapsed:
        # Ẩn nội dung khung sách
        for widget in [entry_id, entry_title, entry_author, entry_year, entry_pages, button_frame]:
            widget.grid_remove()
        for label in frame_books.winfo_children():
            if isinstance(label, CTkLabel) and label != books_title and label != collapse_books_btn:
                label.grid_remove()
        collapse_books_btn.configure(text="▼")
        # Di chuyển khung lên trên cùng
        frame_books.grid(row=1, column=0, padx=10, pady=5, sticky="new")
    else:
        # Hiển thị lại nội dung khung sách
        CTkLabel(frame_books, text="ID Sách:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        entry_id.grid(row=1, column=1, padx=10, pady=5)
        
        CTkLabel(frame_books, text="Tên Sách:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        entry_title.grid(row=2, column=1, padx=10, pady=5)
        
        CTkLabel(frame_books, text="Tác Giả:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        entry_author.grid(row=3, column=1, padx=10, pady=5)
        
        CTkLabel(frame_books, text="Năm Xuất Bản:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        entry_year.grid(row=4, column=1, padx=10, pady=5)
        
        CTkLabel(frame_books, text="Số Trang:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
        entry_pages.grid(row=5, column=1, padx=10, pady=5)
        
        button_frame.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        collapse_books_btn.configure(text="▲")
        
        # Khôi phục vị trí khung
        frame_books.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
    
    # Cập nhật vị trí các khung khác
    update_frames_position()

# Hàm thu gọn/mở rộng khung quản lý độc giả
def toggle_readers_frame():
    global is_readers_collapsed
    is_readers_collapsed = not is_readers_collapsed
    
    if is_readers_collapsed:
        # Ẩn nội dung khung độc giả
        for widget in [entry_reader_id, entry_name, entry_address, entry_phone, entry_email, reader_button_frame]:
            widget.grid_remove()
        for label in frame_readers.winfo_children():
            if isinstance(label, CTkLabel) and label != readers_title and label != collapse_readers_btn:
                label.grid_remove()
        collapse_readers_btn.configure(text="▼")
        # Di chuyển khung vào vị trí phù hợp
        update_frames_position()
    else:
        # Hiển thị lại nội dung khung độc giả
        CTkLabel(frame_readers, text="ID Độc Giả:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        entry_reader_id.grid(row=1, column=1, padx=10, pady=5)
        
        CTkLabel(frame_readers, text="Tên Độc Giả:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        entry_name.grid(row=2, column=1, padx=10, pady=5)
        
        CTkLabel(frame_readers, text="Địa Chỉ:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        entry_address.grid(row=3, column=1, padx=10, pady=5)
        
        CTkLabel(frame_readers, text="Số Điện Thoại:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        entry_phone.grid(row=4, column=1, padx=10, pady=5)
        
        CTkLabel(frame_readers, text="Email:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
        entry_email.grid(row=5, column=1, padx=10, pady=5)
        
        reader_button_frame.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        collapse_readers_btn.configure(text="▲")
        
        # Cập nhật vị trí các khung
        update_frames_position()

# Hàm thu gọn/mở rộng khung quản lý mượn trả
def toggle_borrow_frame():
    global is_borrow_collapsed
    is_borrow_collapsed = not is_borrow_collapsed
    
    if is_borrow_collapsed:
        # Ẩn nội dung khung mượn trả
        for widget in [entry_borrow_reader_id, entry_borrow_book_id, entry_borrow_date, entry_return_date, borrow_button_frame]:
            widget.grid_remove()
        for label in frame_borrow.winfo_children():
            if isinstance(label, CTkLabel) and label != borrow_title and label != collapse_borrow_btn:
                label.grid_remove()
        collapse_borrow_btn.configure(text="▼")
        # Di chuyển khung vào vị trí phù hợp
        update_frames_position()
    else:
        # Hiển thị lại nội dung khung mượn trả
        CTkLabel(frame_borrow, text="ID Độc Giả:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        entry_borrow_reader_id.grid(row=1, column=1, padx=10, pady=5)
        
        CTkLabel(frame_borrow, text="ID Sách:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        entry_borrow_book_id.grid(row=2, column=1, padx=10, pady=5)
        
        CTkLabel(frame_borrow, text="Ngày Mượn:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        entry_borrow_date.grid(row=3, column=1, padx=10, pady=5)
        
        CTkLabel(frame_borrow, text="Ngày Trả:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        entry_return_date.grid(row=4, column=1, padx=10, pady=5)
        
        borrow_button_frame.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        collapse_borrow_btn.configure(text="▲")
        
        # Cập nhật vị trí các khung
        update_frames_position()

# Hàm cập nhật vị trí các khung
def update_frames_position():
    # Xác định vị trí row cho từng khung
    row_books = 1
    row_readers = 2
    row_borrow = 3
    
    # Nếu khung sách thu gọn, đưa nó lên trên cùng
    if is_books_collapsed:
        frame_books.grid(row=row_books, column=0, padx=10, pady=5, sticky="new")
    else:
        frame_books.grid(row=row_books, column=0, padx=10, pady=5, sticky="nsew")
    
    # Nếu khung độc giả thu gọn
    if is_readers_collapsed:
        if is_books_collapsed:
            frame_readers.grid(row=row_books + 1, column=0, padx=10, pady=5, sticky="new")
        else:
            frame_readers.grid(row=row_readers, column=0, padx=10, pady=5, sticky="new")
    else:
        if is_books_collapsed:
            frame_readers.grid(row=row_books + 1, column=0, padx=10, pady=5, sticky="nsew")
        else:
            frame_readers.grid(row=row_readers, column=0, padx=10, pady=5, sticky="nsew")
    
    # Nếu khung mượn trả thu gọn
    if is_borrow_collapsed:
        if is_books_collapsed and is_readers_collapsed:
            frame_borrow.grid(row=row_books + 2, column=0, padx=10, pady=5, sticky="new")
        elif is_books_collapsed or is_readers_collapsed:
            frame_borrow.grid(row=row_readers + 1, column=0, padx=10, pady=5, sticky="new")
        else:
            frame_borrow.grid(row=row_borrow, column=0, padx=10, pady=5, sticky="new")
    else:
        if is_books_collapsed and is_readers_collapsed:
            frame_borrow.grid(row=row_books + 2, column=0, padx=10, pady=5, sticky="nsew")
        elif is_books_collapsed or is_readers_collapsed:
            frame_borrow.grid(row=row_readers + 1, column=0, padx=10, pady=5, sticky="nsew")
        else:
            frame_borrow.grid(row=row_borrow, column=0, padx=10, pady=5, sticky="nsew")

# Tạo giao diện người dùng
root = ctk.CTk()  # Thay thế tk.Tk() bằng ctk.CTk()
root.title("Quản Lý Thư Viện")
root.geometry("2000x1200")  # Kích thước hợp lý hơn
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

logo_path = os.path.join(os.path.dirname(__file__), "assets", "open-book.ico")
root.iconbitmap(logo_path)

# Khung quản lý sách
frame_books = CTkFrame(root)
frame_books.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Tiêu đề section với nút thu gọn
books_title_frame = CTkFrame(frame_books, fg_color="transparent")
books_title_frame.grid(row=0, column=0, columnspan=3, pady=5, padx=5, sticky="ew")
books_title_frame.grid_columnconfigure(0, weight=1)

books_title = CTkLabel(books_title_frame, text="QUẢN LÝ SÁCH", font=("Arial", 16, "bold"))
books_title.grid(row=0, column=0, pady=5, padx=10, sticky="w")

# Nút thu gọn/mở rộng
collapse_books_btn = CTkButton(books_title_frame, text="▲", command=toggle_books_frame, width=30, height=30)
collapse_books_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

# Form nhập thông tin sách
CTkLabel(frame_books, text="ID Sách:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_id = CTkEntry(frame_books, placeholder_text="Nhập ID sách", width=200)
entry_id.grid(row=1, column=1, padx=10, pady=5)

CTkLabel(frame_books, text="Tên Sách:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_title = CTkEntry(frame_books, placeholder_text="Nhập tên sách", width=200)
entry_title.grid(row=2, column=1, padx=10, pady=5)

CTkLabel(frame_books, text="Tác Giả:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_author = CTkEntry(frame_books, placeholder_text="Nhập tên tác giả", width=200)
entry_author.grid(row=3, column=1, padx=10, pady=5)

CTkLabel(frame_books, text="Năm Xuất Bản:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
entry_year = CTkEntry(frame_books, placeholder_text="Nhập năm xuất bản", width=200)
entry_year.grid(row=4, column=1, padx=10, pady=5)

CTkLabel(frame_books, text="Số Trang:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
entry_pages = CTkEntry(frame_books, placeholder_text="Nhập số trang", width=200)
entry_pages.grid(row=5, column=1, padx=10, pady=5)

# Nút chức năng
button_frame = CTkFrame(frame_books)
button_frame.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

add_book = CTkButton(button_frame, text="Thêm Sách", command=add_book, width=100, 
                    fg_color=("#28a745", "#218838"), hover_color=("#218838", "#1e7e34"))
add_book.grid(row=0, column=0, pady=5, padx=5)

delete_book = CTkButton(button_frame, text="Xóa Sách", command=delete_book, width=100,
                       fg_color=("#dc3545", "#c82333"), hover_color=("#c82333", "#bd2130"))
delete_book.grid(row=0, column=1, pady=5, padx=5)

show_books_btn = CTkButton(button_frame, text="Hiển Thị Sách", command=show_books, width=100)
show_books_btn.grid(row=1, column=0, pady=5, padx=5)

edit_book = CTkButton(button_frame, text="Chỉnh Sửa Sách", command=edit_book, width=100,
                      fg_color=("#fd7e14", "#e8710a"), hover_color=("#e8710a", "#d56906"))
edit_book.grid(row=1, column=1, pady=5, padx=5)

# Khung quản lý độc giả
frame_readers = CTkFrame(root)
frame_readers.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

# Tiêu đề section với nút thu gọn
readers_title_frame = CTkFrame(frame_readers, fg_color="transparent")
readers_title_frame.grid(row=0, column=0, columnspan=3, pady=5, padx=5, sticky="ew")
readers_title_frame.grid_columnconfigure(0, weight=1)

readers_title = CTkLabel(readers_title_frame, text="QUẢN LÝ ĐỘC GIẢ", font=("Arial", 16, "bold"))
readers_title.grid(row=0, column=0, pady=5, padx=10, sticky="w")

# Nút thu gọn/mở rộng
collapse_readers_btn = CTkButton(readers_title_frame, text="▲", command=toggle_readers_frame, width=30, height=30)
collapse_readers_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

# Form nhập thông tin độc giả
CTkLabel(frame_readers, text="ID Độc Giả:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_reader_id = CTkEntry(frame_readers, placeholder_text="Nhập ID độc giả", width=200)
entry_reader_id.grid(row=1, column=1, padx=10, pady=5)

CTkLabel(frame_readers, text="Tên Độc Giả:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_name = CTkEntry(frame_readers, placeholder_text="Nhập tên độc giả", width=200)
entry_name.grid(row=2, column=1, padx=10, pady=5)

CTkLabel(frame_readers, text="Địa Chỉ:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_address = CTkEntry(frame_readers, placeholder_text="Nhập địa chỉ", width=200)
entry_address.grid(row=3, column=1, padx=10, pady=5)

CTkLabel(frame_readers, text="Số Điện Thoại:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
entry_phone = CTkEntry(frame_readers, placeholder_text="Nhập số điện thoại", width=200)
entry_phone.grid(row=4, column=1, padx=10, pady=5)

CTkLabel(frame_readers, text="Email:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
entry_email = CTkEntry(frame_readers, placeholder_text="Nhập email", width=200)
entry_email.grid(row=5, column=1, padx=10, pady=5)

# Nút chức năng
reader_button_frame = CTkFrame(frame_readers)
reader_button_frame.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

add_reader = CTkButton(reader_button_frame, text="Thêm Độc Giả", command=add_reader, width=100,
                     fg_color=("#28a745", "#218838"), hover_color=("#218838", "#1e7e34"))
add_reader.grid(row=0, column=0, pady=5, padx=5)

delete_reader = CTkButton(reader_button_frame, text="Xóa Độc Giả", command=delete_reader, width=100,
                        fg_color=("#dc3545", "#c82333"), hover_color=("#c82333", "#bd2130"))
delete_reader.grid(row=0, column=1, pady=5, padx=5)

show_readers_btn = CTkButton(reader_button_frame, text="Hiển Thị Độc Giả", command=show_readers, width=100)
show_readers_btn.grid(row=1, column=0, pady=5, padx=5)

edit_reader = CTkButton(reader_button_frame, text="Chỉnh Sửa Độc Giả", command=edit_reader, width=100,
                      fg_color=("#fd7e14", "#e8710a"), hover_color=("#e8710a", "#d56906"))
edit_reader.grid(row=1, column=1, pady=5, padx=5)

# Khung quản lý mượn trả
frame_borrow = CTkFrame(root)
frame_borrow.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

# Tiêu đề section với nút thu gọn
borrow_title_frame = CTkFrame(frame_borrow, fg_color="transparent")
borrow_title_frame.grid(row=0, column=0, columnspan=3, pady=5, padx=5, sticky="ew")
borrow_title_frame.grid_columnconfigure(0, weight=1)

borrow_title = CTkLabel(borrow_title_frame, text="QUẢN LÝ MƯỢN TRẢ", font=("Arial", 16, "bold"))
borrow_title.grid(row=0, column=0, pady=5, padx=10, sticky="w")

# Nút thu gọn/mở rộng
collapse_borrow_btn = CTkButton(borrow_title_frame, text="▲", command=toggle_borrow_frame, width=30, height=30)
collapse_borrow_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

# Form nhập thông tin mượn trả
CTkLabel(frame_borrow, text="ID Độc Giả:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_borrow_reader_id = CTkEntry(frame_borrow, placeholder_text="Nhập ID độc giả", width=200)
entry_borrow_reader_id.grid(row=1, column=1, padx=10, pady=5)

CTkLabel(frame_borrow, text="ID Sách:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_borrow_book_id = CTkEntry(frame_borrow, placeholder_text="Nhập ID sách", width=200)
entry_borrow_book_id.grid(row=2, column=1, padx=10, pady=5)

CTkLabel(frame_borrow, text="Ngày Mượn:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_borrow_date = CTkEntry(frame_borrow, placeholder_text="YYYY-MM-DD", width=200)
entry_borrow_date.grid(row=3, column=1, padx=10, pady=5)

CTkLabel(frame_borrow, text="Ngày Trả:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
entry_return_date = CTkEntry(frame_borrow, placeholder_text="YYYY-MM-DD", width=200)
entry_return_date.grid(row=4, column=1, padx=10, pady=5)

# Nút chức năng
borrow_button_frame = CTkFrame(frame_borrow)
borrow_button_frame.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

borrow_book_btn = CTkButton(borrow_button_frame, text="Mượn Sách", command=borrow_book, width=100,
                           fg_color=("#28a745", "#218838"), hover_color=("#218838", "#1e7e34"))
borrow_book_btn.grid(row=0, column=0, pady=5, padx=5)

delete_borrow = CTkButton(borrow_button_frame, text="Xóa Mượn Trả", command=delete_borrow, width=100,
                         fg_color=("#dc3545", "#c82333"), hover_color=("#c82333", "#bd2130"))
delete_borrow.grid(row=0, column=1, pady=5, padx=5)

show_borrows_btn = CTkButton(borrow_button_frame, text="Hiển Thị Mượn Trả", command=show_borrows, width=100)
show_borrows_btn.grid(row=1, column=0, pady=5, padx=5)

edit_borrow = CTkButton(borrow_button_frame, text="Chỉnh Sửa Mượn Trả", command=edit_borrow, width=100,
                       fg_color=("#fd7e14", "#e8710a"), hover_color=("#e8710a", "#d56906"))
edit_borrow.grid(row=1, column=1, pady=5, padx=5)

# Khung hiển thị thông tin
frame_right = CTkFrame(root)
frame_right.grid(row=1, column=1, columnspan=20, rowspan=4, padx=10, pady=7, sticky="nsew")
frame_right.grid_rowconfigure(0, weight=1)
frame_right.grid_columnconfigure(0, weight=1)

# Tạo frame chứa tiêu đề hiển thị
title_frame = CTkFrame(frame_right, fg_color="transparent")
title_frame.pack(fill="x", pady=(1, 0))
data_title = CTkLabel(title_frame, text="DỮ LIỆU HIỂN THỊ", font=("Arial", 14, "bold"))
data_title.pack()

# Tạo frame chứa treeview
tree_frame = CTkFrame(frame_right)
tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Thanh cuộn dọc với CustomTkinter
v_scrollbar = CTkScrollbar(tree_frame, orientation="vertical")
v_scrollbar.pack(side="right", fill="y")

# Giữ nguyên treeview vì CustomTkinter không có widget tương đương
tree = ttk.Treeview(tree_frame, yscrollcommand=v_scrollbar.set)
tree.pack(expand=True, fill="both")

style = ttk.Style()
style.configure("Treeview", font=("Arial", 13), rowheight=30)  # Thay đổi kích thước font và chiều cao hàng
style.configure("Treeview.Heading", font=("Arial", 13, "bold")) 

# Liên kết thanh cuộn với Treeview
v_scrollbar.configure(command=tree.yview)

# Khung tìm kiếm
frame_search = CTkFrame(root)
frame_search.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

# Tiêu đề
search_title = CTkLabel(frame_search, text="🔍", font=("Arial", 20, "bold"))
search_title.grid(row=0, column=0, columnspan=1, pady=5, padx=10, sticky="w")

CTkLabel(frame_search, text="Loại:", font=("Arial", 14)).grid(row=0, column=3, sticky="w", padx=2, pady=5)
search_options = ["Sách", "Độc Giả", "Mượn Trả"]
search_combobox = ctk.CTkOptionMenu(frame_search, values=search_options)
search_combobox.grid(row=0, column=4, padx=10, pady=5)
search_combobox.set("Chọn loại")

CTkLabel(frame_search, text="Từ khóa:", font=("Arial", 14)).grid(row=0, column=5, sticky="w", padx=2, pady=5)
search_entry = CTkEntry(frame_search, placeholder_text="Nhập từ khóa tìm kiếm", width=200)
search_entry.grid(row=0, column=7, padx=10, pady=5)

search_button = CTkButton(frame_search, text="Tìm Kiếm", command=search_info, width=100)
search_button.grid(row=0, column=8, padx=10, pady=5)

# Nút Crawl Dữ Liệu
crawl_button = CTkButton(frame_search, text="Crawl Dữ Liệu ⬇", command=threaded_crawl_data, 
                         width=120, fg_color=("#17a2b8", "#138496"), hover_color=("#138496", "#117a8b"))
crawl_button.grid(row=0, column=9, pady=5, padx=10, sticky="e")

# Nút Hồ Sơ
profile_button = CTkButton(frame_search, text="Hồ Sơ   👤", command=create_profile_window, 
                          width=100, fg_color=("#6c757d", "#5a6268"), hover_color=("#5a6268", "#4e555b"))
profile_button.grid(row=0, column=13, padx=250, pady=5, sticky="e")

# Cấu hình disable state cho các nút
add_book.configure(state="disabled")
delete_book.configure(state="disabled")
edit_book.configure(state="disabled")
add_reader.configure(state="disabled")
delete_reader.configure(state="disabled")
edit_reader.configure(state="disabled")
delete_borrow.configure(state="disabled")
edit_borrow.configure(state="disabled")
crawl_button.configure(state="disabled")

def __main__():
    # Khởi tạo các biến theo dõi trạng thái thu gọn
    global is_books_collapsed, is_readers_collapsed, is_borrow_collapsed
    is_books_collapsed = False
    is_readers_collapsed = False
    is_borrow_collapsed = False
    
    create_login_window()
    root.mainloop()
    
if __name__ == "__main__":
    __main__()