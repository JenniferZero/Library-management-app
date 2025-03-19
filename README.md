# Library Management App

A library management application with user authentication, book management, and data crawling features.

## Installation

### Step 1: Clone the repository

```sh
git clone https://github.com/yourusername/library-management-app.git
cd library-management-app
```

### Step 2: Install dependencies

Make sure you have Python 3.6 or higher installed. Then, install the required dependencies:

```sh
pip install -r requirements.txt
```

### Step 3: Download the NLP model

The application uses the `en_core_web_sm` model from spaCy. Download the model using the following command:

```sh
python -m spacy download en_core_web_sm
```

### Step 4: Package the application

Create a source distribution of the application:

```sh
python setup.py sdist
```

### Step 5: Install the application

Install the application locally:

```sh
pip install .
```

## Running the Application

After installing the application, you can run it using the console script defined in `setup.py`:

```sh
library-manager
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