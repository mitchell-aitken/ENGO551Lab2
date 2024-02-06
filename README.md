# ENGO 551
# Lab 2 Book Review Web App

This web application has been enhanced from Project 1 to include integration with the Google Books API, allowing users to access a broader range of information about books, including ratings from a wider audience. Users can search for books, view detailed information, submit reviews, and see ratings from Google Books.

Some additional styling has been done to this website, and allowing logged in users to review a book once.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Acknowledgments](#acknowledgments)

## Features

- User registration and authentication
- Book search functionality
- Viewing book details and reviews
- Submitting book reviews
- Google Books API Integration

## Getting Started

### Prerequisites

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Requests Requests (for Google Books API requests)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mitchell-aitken/lab2/

2. Install the *NEW* required dependencies (added a few that differ from the original):
    ```bash
    pip install -r requirements.txt

### Usage
1. **Run the Flask application:**

   ```bash
   $env:FLASK_app = "application.py"
   flask run

## Acknowledgements

- **OpenAI:** Special thanks to [OpenAI](https://www.openai.com/) for providing the GPT-3.5 model used for natural language processing in this project.
- **Google Books API** For offering an extensive database of book information and reviews.