# Flask Data Server App

## Project Description

This Flask application serves as a data server, providing RESTful APIs to interact with a MySQL database. It's designed to support a larger application by handling database operations.

## Installation

To set up the project:

1. Clone the repository:
git clone <repository-url>

2. Navigate to the project directory:
cd <project-directory>

3. Install dependencies:
pip install -r requirements.txt


## Usage

To run the application:

1. Start the Flask server:
python app.py

2. The server will start on `localhost` at the default port `5000`.

## API Endpoints

- `GET /getComments`: Fetch comments for a given post.
- `GET /getPostsWithCommentIdsAndUpvotes`: Fetch posts with comments and upvotes.
