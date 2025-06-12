# Library Management App

A modern library management application with user authentication, book and reader management, and the ability to crawl and update book data automatically.


## Features

- **User Authentication**: Secure login for different user roles.
- **Book Management**: Add, update, delete, and search for books in your library.
- **Reader Management**: Manage reader information and borrowing activities.
- **Borrowing System**: Track which readers have borrowed which books and due dates.
- **Data Crawling**: Automatically fetch and update book data from external sources using asynchronous crawling and progress tracking.
- **Persistent Storage**: Uses JSON files to store all relevant data for users, books, readers, and borrow records.

## How It Works

1. **Authentication**: Users log in to the system to access library features.
2. **Book/Reader Management**: Admins can add, edit, or remove books and readers. Readers can search for available books.
3. **Borrow and Return**: The app tracks which books are borrowed, by whom, and manages return dates.
4. **Data Crawling**: The app can fetch book information from external sources and update the local database, providing a progress bar and allowing task cancellation.
5. **Data Storage**: All data is saved in JSON files under `src/data/`.


## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/JenniferZero/Library-management-app.git
cd Library-management-app
```

### 2. Set Up a Virtual Environment (Optional)

#### On Windows:
```sh
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```
_or, if using `setup.py`:_
```sh
pip install .
```


## Running the Application

1. **Navigate to the source directory:**

    ```sh
    cd src
    ```

2. **Run the application:**

    ```sh
    python library_manager.py
    ```

## Data Files

The app uses several JSON files in the `src/data/` directory:

- `users.json`: Stores user information.
- `books.json`: Stores book details.
- `readers.json`: Stores reader information.
- `borrow.json`: Stores borrowing records.

Make sure these files exist before running the app. If missing, create empty JSON files with those names.


## Packaging

To package the application:

```sh
python setup.py sdist bdist_wheel
```

## Notes

- The application requires Python 3.6 or newer.
- Main dependencies: `aiohttp`, `spacy`, `beautifulsoup4`, `jsonschema`.
- For any issues or contributions, please open an issue or pull request on GitHub.


## Members
- `Nguyen Huu Thang`
- `Nguyen Ngoc Son`
