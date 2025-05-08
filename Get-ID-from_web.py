import requests
import re

def fetch_filtered_book_urls(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Không thể lấy dữ liệu từ URL")
        return []
    
    data = response.json()
    book_urls = []
    
    if 'works' in data:
        for work in data['works']:
            if 'key' in work:
                match = re.search(r'"(OL\d+W)"', f'"{work["key"].split("/")[-1]}"')
                if match:
                    book_id = match.group(1)
                    full_url = f"https://openlibrary.org/works/{book_id}"
                    book_urls.append(full_url)
    
    return book_urls

url = "https://openlibrary.org/subjects/romance.json?limit=50" 
# Thể loại: mystery, history, romance, fiction, fantasy, horror, thriller, adventure, biography, poetry
# Thay đổi limit để lấy nhiều hoặc ít sách hơn


filtered_book_urls = fetch_filtered_book_urls(url)
print(filtered_book_urls)

# Lưu các URL vào file văn bản
with open('src/data/book_urls.txt', 'a') as file:
    for book_url in filtered_book_urls:
        file.write(f"{book_url}\n")
    print(f"Đã ghi {len(filtered_book_urls)} URL vào file book_urls.txt")