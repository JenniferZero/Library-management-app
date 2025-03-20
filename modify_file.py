import requests
import json
from collections import Counter

def fetch_data(url):
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def process_data(data):
    books, subjects = [], []
    for book in data.get("works", []):
        if "subject" in book and book.get("cover_edition_key"):
            title = book.get("title", "Unknown Title")
            cover_edition_key = book.get("cover_edition_key", "N/A")
            subject_list = book.get("subject", [])
            books.append({"title": title, "cover_edition_key": cover_edition_key, "subjects": subject_list})
            subjects.extend(subject_list)
    return books, subjects

def analyze_subjects(subjects):
    subject_counts = Counter(subjects)
    sorted_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
    return [subj[0] for subj in sorted_subjects[:3]] or [subjects[0]]

def assign_main_subjects(books, top_subjects):
    for book in books:
        book["main_subjects"] = [subj for subj in book["subjects"] if subj in top_subjects] or [book["subjects"][0]]
        del book["subjects"]
    return books

def save_to_file(data, filename="data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    url = "https://openlibrary.org/subjects/history.json?limit=10"
    raw_data = fetch_data(url)
    if raw_data:
        books, subjects = process_data(raw_data)
        top_subjects = analyze_subjects(subjects)
        books = assign_main_subjects(books, top_subjects)
        save_to_file(books)
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()