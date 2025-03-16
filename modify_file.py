import json
import random

# Đọc dữ liệu từ file books.json
with open('d:\\Downloads\\Project Python\\data\\books.json', 'r', encoding='utf-8') as books_file:
    books_data = json.load(books_file)

# Lấy danh sách các book_id từ books.json
book_ids = [book['id'] for book in books_data]

# Đọc dữ liệu từ file borrow.json
with open('d:\\Downloads\\Project Python\\data\\borrow.json', 'r', encoding='utf-8') as borrow_file:
    borrow_data = json.load(borrow_file)

# Sửa thông tin book_id trong borrow.json
for borrow in borrow_data:
    borrow['book_id'] = random.sample(book_ids, min(5, len(book_ids)))

# Ghi dữ liệu đã sửa vào file borrow.json
with open('d:\\Downloads\\Project Python\\data\\borrow.json', 'w', encoding='utf-8') as borrow_file:
    json.dump(borrow_data, borrow_file, ensure_ascii=False, indent=4)

print("Đã cập nhật thông tin book_id trong borrow.json")
