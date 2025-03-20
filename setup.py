from setuptools import setup, find_packages

setup(
    name="LibraryManagementApp",
    version="1.0.0",
    author="JenniferZero",
    author_email="nhthang312@gmail.com",
    description="A library management application with user authentication, book management, and data crawling features.",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "aiohttp",
        "spacy",
        "beautifulsoup4",
        "jsonschema"  # Add any other dependencies as needed
    ],
    entry_points={
        'console_scripts': [
            'library-manager=Library_Manager:main',  # Adjust if you have a main function
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)