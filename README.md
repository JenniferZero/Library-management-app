# Library Management App

A library management application with user authentication, book management, and data crawling features.

---

## Installation

### Step 1: Clone the repository

Clone the project repository to your local machine:

```sh
git clone https://github.com/JenniferZero/Library-management-app.git
cd Library-management-app
```

---

### Step 2: Set up a virtual environment (optional but recommended)

Create and activate a virtual environment to isolate dependencies:

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

---

### Step 3: Install dependencies

Install all required dependencies from the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

If some dependencies are missing, install them manually:

```sh
pip install aiohttp beautifulsoup4
```

---

## Running the Application

### Step 1: Navigate to the source directory

```sh
cd src
```

### Step 2: Run the application

Run the application using Python:

```sh
python library_manager.py
```

---

## Data Files

The application uses several JSON files to store data. These files are located in the `src/data` directory:

- `users.json`: Stores user information.
- `books.json`: Stores book information.
- `readers.json`: Stores reader information.
- `borrow.json`: Stores borrowing records.

Make sure these files are present in the `src/data` directory before running the application. If they are missing, create empty JSON files with the same names.

---

## Packaging the Application

To package the application into a standalone executable file, follow these steps:

### Step 1: Install PyInstaller

Install PyInstaller using pip:

```sh
pip install pyinstaller
```

### Step 2: Package the application

Run the following command to package the application:

```sh
pyinstaller --name LibraryManager --onefile --noconsole --clean --noconfirm `
--hidden-import=aiohttp --hidden-import=bs4 --hidden-import=tkinter `
--add-data "data;data" --add-data "assets;assets" --icon "assets/open-book.ico" `
--distpath "dist" --log-level DEBUG library_manager.py
```
To repackage the app, delete the `build` folder and the old `.exe` file.

### Step 3: Locate the executable

After the packaging process is complete, the executable file (`LibraryManager.exe`) will be located in the `dist` directory
---

## Notes

- Ensure that all required data files are included in the `data` directory when running or packaging the application.
- If you encounter any issues during packaging, refer to the PyInstaller documentation or check the terminal logs for detailed error messages.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
