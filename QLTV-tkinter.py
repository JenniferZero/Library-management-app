from tkinter import ttk
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import json
import os

# Định nghĩa thư mục chứa dữ liệu JSON
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

# Đường dẫn tới các file JSON
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.json')
READERS_FILE = os.path.join(DATA_DIR, 'readers.json')
BORROW_FILE = os.path.join(DATA_DIR, 'borrow.json')

# Hàm đọc dữ liệu từ file JSON
def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Hàm ghi dữ liệu vào file JSON
def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Hàm chuyển đổi chuỗi ID từ bàn phím thành danh sách các số nguyên
def parse_ids(id_input):
    # Loại bỏ khoảng trắng thừa
    id_input = id_input.strip()
    try:
        # Nếu có dấu phẩy, tách thành danh sách, ngược lại trả về danh sách chứa 1 phần tử
        return [x.strip() for x in id_input.split(',')]
    except ValueError:
        return None

# Hàm kiểm tra định dạng ngày tháng
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

# Hàm tạo cửa sổ đăng nhập
def create_login_window():
    global login_window, entry_username, entry_password
    root.withdraw()  # Ẩn cửa sổ chính
    
    login_window = tk.Toplevel()
    login_window.title("Đăng Nhập")
    login_window.geometry("80000x12000")
    
    tk.Label(login_window, text="Tên đăng nhập:").pack(pady=10)
    entry_username = tk.Entry(login_window)
    entry_username.pack(pady=5)
    
    tk.Label(login_window, text="Mật khẩu:").pack(pady=10)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)
    
    tk.Button(login_window, text="Đăng nhập", command=login).pack(pady=20)


# Hàm đăng nhập
def login():
    username = entry_username.get()
    password = entry_password.get()

    users = read_json(USERS_FILE)
    for user in users:
        if user["username"] == username and user["password"] == password:
            messagebox.showinfo("Thành công", f"Đăng nhập thành công với quyền {user['role']}.")
            root.deiconify()
            login_window.destroy()
            if user["role"] == "admin":
                enable_admin_features()
            return

    messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng.")

# Hàm kích hoạt các tính năng của admin
def enable_admin_features():
    add_book.config(state=tk.NORMAL)
    delete_book.config(state=tk.NORMAL)
    edit_book.config(state=tk.NORMAL)
    add_reader.config(state=tk.NORMAL)
    delete_reader.config(state=tk.NORMAL)
    edit_reader.config(state=tk.NORMAL)
    delete_borrow.config(state=tk.NORMAL)
    edit_borrow.config(state=tk.NORMAL)


# Hàm thêm sách mới
def add_book():
    book_id = entry_id.get()
    title = entry_title.get()
    author = entry_author.get()
    year = entry_year.get()
    genre = entry_genre.get()
    quantity = entry_quantity.get()

    if not title or not author or not year or not genre or not quantity:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sách.")
        return

    if not validate_int(year):
        messagebox.showerror("Lỗi", "Năm xuất bản phải là số nguyên.")
        return

    if not validate_int(quantity):
        messagebox.showerror("Lỗi", "Số lượng phải là số nguyên.")
        return
    
    books = read_json(BOOKS_FILE)
    new_book = {
        "id": book_id,
        "title": title,
        "author": author,
        "year": int(year),
        "genre": genre,
        "quantity": int(quantity)
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

# Hàm xóa sách (cho phép nhập nhiều định dạng ID)
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

# Hàm xóa độc giả (cho phép nhập nhiều định dạng ID)
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
    entry_genre.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
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
    genre = entry_genre.get()
    quantity = entry_quantity.get()

    if not book_id or not title or not author or not year or not genre or not quantity:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sách.")
        return

    books = read_json(BOOKS_FILE)
    for book in books:
        if book["id"] == book_id:
            book["title"] = title
            book["author"] = author
            book["year"] = int(year)
            book["genre"] = genre
            book["quantity"] = int(quantity)
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

    # Định dạng cột
    tree["columns"] = ("ID", "Tên Sách", "Tác Giả", "Năm", "Thể Loại", "Số Lượng")
    tree.column("#0", width=0, stretch=tk.NO)  # Cột ẩn
    tree.column("ID", anchor=tk.W, width=10)
    tree.column("Tên Sách", anchor=tk.W, width=150)
    tree.column("Tác Giả", anchor=tk.W, width=50)
    tree.column("Năm", anchor=tk.CENTER, width=10)
    tree.column("Thể Loại", anchor=tk.W, width=50)
    tree.column("Số Lượng", anchor=tk.CENTER, width=10)

    # Tiêu đề cột
    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("ID", text="ID", anchor=tk.W)
    tree.heading("Tên Sách", text="Tên Sách", anchor=tk.W)
    tree.heading("Tác Giả", text="Tác Giả", anchor=tk.W)
    tree.heading("Năm", text="Năm", anchor=tk.CENTER)
    tree.heading("Thể Loại", text="Thể Loại", anchor=tk.W)
    tree.heading("Số Lượng", text="Số Lượng", anchor=tk.CENTER)

    # Thêm dữ liệu vào bảng
    for book in books:
        tree.insert("", tk.END, values=(book["id"], book["title"], book["author"], 
                                         book["year"], book["genre"], book["quantity"]))

# Hàm hiển thị thông tin độc giả
def show_readers():
    readers = read_json(READERS_FILE)
    clear_entries()
    clear_display()

    tree["columns"] = ("ID", "Tên", "Địa Chỉ", "SĐT", "Email")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ID", anchor=tk.W, width=20)
    tree.column("Tên", anchor=tk.W, width=150)
    tree.column("Địa Chỉ", anchor=tk.W, width=100)
    tree.column("SĐT", anchor=tk.CENTER, width=100)
    tree.column("Email", anchor=tk.W, width=200)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("ID", text="ID", anchor=tk.W)
    tree.heading("Tên", text="Tên", anchor=tk.W)
    tree.heading("Địa Chỉ", text="Địa Chỉ", anchor=tk.W)
    tree.heading("SĐT", text="SĐT", anchor=tk.CENTER)
    tree.heading("Email", text="Email", anchor=tk.W)

    for reader in readers:
        tree.insert("", tk.END, values=(reader["id"], reader["name"], reader["address"], 
                                         reader["phone"], reader["email"]))

# Hàm hiển thị thông tin mượn sách
def show_borrows():
    borrows = read_json(BORROW_FILE)
    clear_entries()
    clear_display()

    tree["columns"] = ("ID Độc Giả", "ID Sách", "Ngày Mượn", "Ngày Trả")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ID Độc Giả", anchor=tk.W, width=10)
    tree.column("ID Sách", anchor=tk.W, width=50)
    tree.column("Ngày Mượn", anchor=tk.CENTER, width=120)
    tree.column("Ngày Trả", anchor=tk.CENTER, width=120)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("ID Độc Giả", text="ID Độc Giả", anchor=tk.W)
    tree.heading("ID Sách", text="ID Sách", anchor=tk.W)
    tree.heading("Ngày Mượn", text="Ngày Mượn", anchor=tk.CENTER)
    tree.heading("Ngày Trả", text="Ngày Trả", anchor=tk.CENTER)

    for borrow in borrows:
        tree.insert("", tk.END, values=(borrow["reader_id"], borrow["book_id"], 
                                         borrow["borrow_date"], borrow["return_date"]))

# Hàm tìm kiếm thông tin
def search_info():
    search_type = search_combobox.get()
    keyword = search_entry.get().strip().lower()

    if not keyword:
        messagebox.showerror("Lỗi", "Vui lòng nhập từ khóa tìm kiếm.")
        return

    if search_type == "Sách":
        items = read_json(BOOKS_FILE)
        results = [item for item in items if keyword in item["title"].lower() or keyword in item["author"].lower() or keyword in item["genre"].lower() or keyword == str(item["id"]).lower() or keyword == str(item["year"]).lower() or keyword == str(item["quantity"]).lower()]
    elif search_type == "Độc Giả":
        items = read_json(READERS_FILE)
        results = [item for item in items if keyword in item["name"].lower() or keyword in item["address"].lower() or keyword in item["phone"].lower() or keyword in item["email"].lower() or keyword == str(item["id"]).lower()]
    elif search_type == "Mượn Trả":
        items = read_json(BORROW_FILE)
        results = [item for item in items if keyword == str(item["reader_id"]).lower() or keyword == str(item["book_id"]).lower() or keyword == item["borrow_date"].lower() or keyword == item["return_date"].lower()]
    else:
        messagebox.showerror("Lỗi", "Vui lòng chọn loại thông tin cần tìm kiếm.")
        return

    clear_display()
    if search_type == "Sách":
        tree["columns"] = ("ID", "Tên Sách", "Tác Giả", "Năm", "Thể Loại", "Số Lượng")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("ID", anchor=tk.W, width=50)
        tree.column("Tên Sách", anchor=tk.W, width=150)
        tree.column("Tác Giả", anchor=tk.W, width=100)
        tree.column("Năm", anchor=tk.CENTER, width=50)
        tree.column("Thể Loại", anchor=tk.W, width=100)
        tree.column("Số Lượng", anchor=tk.CENTER, width=50)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("ID", text="ID", anchor=tk.W)
        tree.heading("Tên Sách", text="Tên Sách", anchor=tk.W)
        tree.heading("Tác Giả", text="Tác Giả", anchor=tk.W)
        tree.heading("Năm", text="Năm", anchor=tk.CENTER)
        tree.heading("Thể Loại", text="Thể Loại", anchor=tk.W)
        tree.heading("Số Lượng", text="Số Lượng", anchor=tk.CENTER)

        for item in results:
            tree.insert("", tk.END, values=(item["id"], item["title"], item["author"], item["year"], item["genre"], item["quantity"]))
    elif search_type == "Độc Giả":
        tree["columns"] = ("ID", "Tên", "Địa Chỉ", "SĐT", "Email")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("ID", anchor=tk.W, width=50)
        tree.column("Tên", anchor=tk.W, width=150)
        tree.column("Địa Chỉ", anchor=tk.W, width=150)
        tree.column("SĐT", anchor=tk.CENTER, width=100)
        tree.column("Email", anchor=tk.W, width=100)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("ID", text="ID", anchor=tk.W)
        tree.heading("Tên", text="Tên", anchor=tk.W)
        tree.heading("Địa Chỉ", text="Địa Chỉ", anchor=tk.W)
        tree.heading("SĐT", text="SĐT", anchor=tk.CENTER)
        tree.heading("Email", text="Email", anchor=tk.W)

        for item in results:
            tree.insert("", tk.END, values=(item["id"], item["name"], item["address"], item["phone"], item["email"]))
    elif search_type == "Mượn Trả":
        tree["columns"] = ("ID Độc Giả", "ID Sách", "Ngày Mượn", "Ngày Trả")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("ID Độc Giả", anchor=tk.W, width=100)
        tree.column("ID Sách", anchor=tk.W, width=100)
        tree.column("Ngày Mượn", anchor=tk.CENTER, width=120)
        tree.column("Ngày Trả", anchor=tk.CENTER, width=120)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("ID Độc Giả", text="ID Độc Giả", anchor=tk.W)
        tree.heading("ID Sách", text="ID Sách", anchor=tk.W)
        tree.heading("Ngày Mượn", text="Ngày Mượn", anchor=tk.CENTER)
        tree.heading("Ngày Trả", text="Ngày Trả", anchor=tk.CENTER)

        for item in results:
            tree.insert("", tk.END, values=(item["reader_id"], item["book_id"], item["borrow_date"], item["return_date"]))

# Hàm xóa thông tin hiển thị
def clear_display():
    for item in tree.get_children():
        tree.delete(item)
        
# Tạo giao diện người dùng
root = tk.Tk()
root.title("Quản Lý Thư Viện")
root.geometry("80000x12000")

# Khung quản lý sách
frame_books = tk.LabelFrame(root, text="Quản Lý Sách", padx=5, pady=10)
frame_books.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")

tk.Label(frame_books, text="ID Sách").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_id = tk.Entry(frame_books)
entry_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_books, text="Tên Sách").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_title = tk.Entry(frame_books)
entry_title.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_books, text="Tác Giả").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_author = tk.Entry(frame_books)
entry_author.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_books, text="Năm Xuất Bản").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_year = tk.Entry(frame_books)
entry_year.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_books, text="Thể Loại").grid(row=4, column=0, sticky="w", padx=5, pady=5)
entry_genre = tk.Entry(frame_books)
entry_genre.grid(row=4, column=1, padx=5, pady=5)

tk.Label(frame_books, text="Số Lượng").grid(row=5, column=0, sticky="w", padx=5, pady=5)
entry_quantity = tk.Entry(frame_books)
entry_quantity.grid(row=5, column=1, padx=5, pady=5)

tk.Button(frame_books, text="Thêm Sách", command=add_book).grid(row=6, column=0, pady=2, padx=5)
tk.Button(frame_books, text="Xóa Sách", command=delete_book).grid(row=6, column=1, pady=2, padx=5)
tk.Button(frame_books, text="Hiển Thị Sách", command=show_books).grid(row=7, column=0, pady=2, padx=5)
tk.Button(frame_books, text="Chỉnh Sửa Sách", command=edit_book).grid(row=7, column=1, pady=2, padx=5)

# Khung quản lý độc giả
frame_readers = tk.LabelFrame(root, text="Quản Lý Độc Giả", padx=5, pady=10)
frame_readers.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

tk.Label(frame_readers, text="ID Độc Giả").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_reader_id = tk.Entry(frame_readers)
entry_reader_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_readers, text="Tên Độc Giả").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_name = tk.Entry(frame_readers)
entry_name.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_readers, text="Địa Chỉ").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_address = tk.Entry(frame_readers)
entry_address.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_readers, text="Số Điện Thoại").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_phone = tk.Entry(frame_readers)
entry_phone.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_readers, text="Email").grid(row=4, column=0, sticky="w", padx=5, pady=5)
entry_email = tk.Entry(frame_readers)
entry_email.grid(row=4, column=1, padx=5, pady=5)

tk.Button(frame_readers, text="Thêm Độc Giả", command=add_reader).grid(row=5, column=0, pady=2, padx=5)
tk.Button(frame_readers, text="Xóa Độc Giả", command=delete_reader).grid(row=5, column=1, pady=2, padx=5)
tk.Button(frame_readers, text="Hiển Thị Độc Giả", command=show_readers).grid(row=6, column=0, pady=2, padx=5)
tk.Button(frame_readers, text="Chỉnh Sửa Độc Giả", command=edit_reader).grid(row=6, column=1, pady=2, padx=5)

# Khung quản lý mượn trả
frame_borrow = tk.LabelFrame(root, text="Quản Lý Mượn Trả", padx=5, pady=10)
frame_borrow.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

tk.Label(frame_borrow, text="ID Độc Giả").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_borrow_reader_id = tk.Entry(frame_borrow)
entry_borrow_reader_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_borrow, text="ID Sách").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_borrow_book_id = tk.Entry(frame_borrow)
entry_borrow_book_id.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_borrow, text="Ngày Mượn").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_borrow_date = tk.Entry(frame_borrow)
entry_borrow_date.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_borrow, text="Ngày Trả").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_return_date = tk.Entry(frame_borrow)
entry_return_date.grid(row=3, column=1, padx=5, pady=5)

tk.Button(frame_borrow, text="Mượn Sách", command=borrow_book).grid(row=4, column=0, pady=2, padx=5)
tk.Button(frame_borrow, text="Xóa Mượn Trả", command=delete_borrow).grid(row=4, column=1, pady=2, padx=5)
tk.Button(frame_borrow, text="Hiển Thị Mượn Trả", command=show_borrows).grid(row=5, column=0, pady=2, padx=5)
tk.Button(frame_borrow, text="Chỉnh Sửa Mượn Trả", command=edit_borrow).grid(row=5, column=1, pady=2, padx=5)

# Khung hiển thị thông tin
frame_right = tk.Frame(root)
frame_right.grid(row=1, column=1, columnspan= 2, rowspan=10, padx=5, pady=10, sticky="nsew")

# Khung tìm kiếm
frame_search = tk.Frame(root, padx=360, pady=2)
frame_search.grid(row=0, column=1, columnspan=2, padx=0, pady=0, sticky="ew")

tk.Label(frame_search, text="Tìm Kiếm Theo").grid(row=0, column=0, sticky="w", padx=5, pady=5)
search_combobox = ttk.Combobox(frame_search, values=["Sách", "Độc Giả", "Mượn Trả"])
search_combobox.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_search, text="Từ Khóa").grid(row=0, column=2, sticky="w", padx=5, pady=5)
search_entry = tk.Entry(frame_search)
search_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Button(frame_search, text="Tìm Kiếm", command=search_info).grid(row=0, column=4, padx=5, pady=5)


# Tạo Treeview hiển thị trong frame_right
tree = ttk.Treeview(frame_right)
tree.pack(expand=True, fill="both")

root.mainloop()
