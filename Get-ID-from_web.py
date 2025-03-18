import requests
import re

def fetch_filtered_book_ids(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Không thể lấy dữ liệu từ URL")
        return []
    
    data = response.json()
    book_ids = []
    
    if 'works' in data:
        for work in data['works']:
            if 'key' in work:
                match = re.search(r'"(OL\d+W)"', f'"{work["key"].split("/")[-1]}"')
                if match:
                    book_ids.append(match.group(1))
    
    return book_ids

url = "https://openlibrary.org/subjects/mystery.json?limit=50"
filtered_book_ids = fetch_filtered_book_ids(url)
print(filtered_book_ids)