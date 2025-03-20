# Library Management App

A library management application with user authentication, book management, and data crawling features.

## Installation

### Step 1: Clone the repository

```sh
git clone https://github.com/JenniferZero/Library-management-app.git
cd library-management-app
```

### Step 2: Install dependencies

Make sure you have Python 3.6 or higher installed. Then, install the required dependencies:

```sh
pip install -r requirements.txt
```

### Step 3: Install `thinc` and `spacy`

You may need to install `thinc` and `spacy` separately if they are not included in your `requirements.txt`:

```sh
pip install thinc 
pip install spacy==3.5.0
```

### Step 4: Download the NLP model

The application uses the `en_core_web_sm` model from spaCy. Download the model using the following command:

```sh
python -m spacy download en_core_web_sm
```

### Step 5: Install C++ Build Tools

For Windows users, you need to install the following components:

1. **C++ Build Tools**:
    - Download and install the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

2. **Windows 10 SDK** (or Windows 11 SDK if you are using Windows 11):
    - During the installation of the C++ Build Tools, make sure to select the "Windows 10 SDK" or "Windows 11 SDK" component.

3. **MSVC v142 - VS 2019 C++ x64/x86 build tools**:
    - Ensure that the "MSVC v142 - VS 2019 C++ x64/x86 build tools" component is selected during the installation.

4. **C++ CMake tools for Windows**:
    - Also, select the "C++ CMake tools for Windows" component.

### Step 6: Package the application

Create a source distribution of the application:

```sh
python setup.py sdist
```

### Step 7: Install the application

Install the application locally:

```sh
pip install .
```

## Running the Application

After installing the application, you can run it using the following command:

```sh
cd src
python library_manager.py
```

## Data Files

The application uses several JSON files to store data. These files are located in the `src/data` directory:

- `users.json`: Stores user information.
- `books.json`: Stores book information.
- `readers.json`: Stores reader information.
- `borrow.json`: Stores borrowing records.
- `keywords.txt`: Stores keywords for genre prediction.

Make sure these files are present in the `src/data` directory before running the application.

## Usage

The application provides the following features:

- User authentication
- Book management (add, delete, edit books)
- Reader management (add, delete, edit readers)
- Borrowing management (add, delete, edit borrowing records)
- Data crawling for book information

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Packed App

To package files into an app use the command:

```sh
pyinstaller --name library_manager --onefile --noconsole --hidden-import spacy.lang.en --add-data "src/data;data" src/library_manager.py
```