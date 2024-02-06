# RealTalkTech

## Description
RealTalkTech is a dynamic social media platform designed for SaaS procurement. It allows users to create profiles, post content under various tech categories, comment, upvote, and engage with a community passionate about software buying. The platform is built with Flask and features robust RESTful APIs, backed by a MySQL database.

## Setup Instructions

### Prerequisites
- Python 3.x
- Docker
- Git (for cloning the repository)

### Clone the Repository
1. Clone the repository and Install Required Packages:
   ```bash
   git clone <repository-url>
   cd realtalktech-mono-service
   pip install -r requirements.txt

### Setting Up a Local Testing Environment with Docker
To set up a local MySQL instance for testing:
1. Ensure Docker is installed and running on your machine.
2. Run the following command inside the stackTemplates/docker folder:
   ```bash
   docker-compose up -d
   ```
3. This sets up a MySQL database accessible at `localhost:3306`.
4. ssh into your local MySQL instance and populate tables. From the project directory:
    ```bash
    chmod +x dbScripts/testConnect.sh
    ./dbScripts/testConnect.sh
    ```
5. From the MySQL connection:
    ```bash
    source dbScripts/initDb.sql
    source dbScripts/verify_tables_exist.sql
    ```

### Configuration Modes
RealTalkTech operates in three modes:
- **Production Mode**: Connects to the production database. Suitable for deployment.
- **Development Mode**: Ideal for development with debug and verbose output enabled. (Coming Soon)
- **Testing Mode**: Uses a local MySQL instance for testing, ensuring isolation from production data.

To switch between these modes, set the appropriate configuration when initializing the app:
- For Production: `create_app(config_class=ProductionConfig)`
- For Development: `create_app(config_class=DevelopmentConfig)`
- For Testing: `create_app(config_class=TestingConfig)`

For now, there is a specific test_app.py file. Be sure to import that if you are electing to use the app for testing.

# API Documentation

## Get Feed API

### Description
The Get Feed API retrieves a paginated list of posts from the RealTalkTech platform. It supports fetching posts either from a specific category or from all categories a user is interested in. Each post includes details like title, body, creation and update timestamps, associated vendors, and categories. It also indicates the current user's vote on the post (upvote, no vote, or not applicable).

### Request
- **Endpoint**: `GET /feed`
- **Parameters**:
  - `categoryId` (int, optional): The ID of the category from which to fetch posts. If omitted, posts from all categories the user is interested in are fetched.
  - `userId` (int, required): The ID of the user making the request.
  - `page` (int, default=1): The page number for pagination.
  - `count` (int, default=10): The number of posts to return per page.

### Example Request
```http
GET /feed?categoryId=1&userId=123&page=1&count=10
```

### Response
- **metadata**: Object containing request parameters for reference.
- **posts**: An array of post objects. Each post contains:
  - `post_id`: Post ID.
  - `title`: Title of the post.
  - `body`: Body content of the post.
  - `created_timestamp`: ISO formatted creation timestamp.
  - `updated_timestamp`: ISO formatted update timestamp.
  - `user_id`: ID of the user who created the post.
  - `vendors`: Comma-separated list of vendors associated with the post.
  - `categories`: Array of categories the post belongs to.
  - `user_vote`: Indicates the current user's vote on the post (true for upvote, null for no vote or not applicable).

### Example Response
```json
{
  "metadata": {
    "categoryId": 1,
    "author_user_id": 123,
    "page": 1,
    "count": 10
  },
  "posts": [
    {
      "id": 101,
      "title": "Latest Tech Trends",
      "body": "Discussion on the latest in tech...",
      "created_timestamp": "2023-01-01T12:00:00",
      "updated_timestamp": "2023-01-02T15:00:00",
      "user_id": 45,
      "vendors": "TechCorp, InnovateInc",
      "categories": ["Technology", "Innovation"],
      "user_vote": true
    },
    // ... more posts ...
  ]
}
```
## Get Comments API

### Description
The Get Comments API fetches a paginated list of comments for a specific post. Each comment includes the commenter's ID and username, the comment text, total upvotes, and the current user's vote on the comment.

### Request
- **Endpoint**: `GET /getCommentsForPost`
- **Parameters**:
  - `postId` (int, required): The ID of the post for which comments are being fetched.
  - `userId` (int, required): The ID of the user making the request.
  - `page` (int, default=1): The page number for pagination.
  - `count` (int, default=10): The number of comments to return per page.

### Example Request
```http
GET /getComments?postId=123&userId=456&page=1&count=10
```

### Response
- **metadata**: Object containing request parameters for reference.
- **comments**: An array of comment objects. Each comment contains:
  - `comment_id`: Comment ID.
  - `user`: Object with `id` and `username` of the commenter.
  - `text`: Comment text.
  - `total_upvotes`: Total number of upvotes for the comment.
  - `user_vote`: Current user's vote on the comment (true for upvote, null for no vote).
  - `createdTimestamp`: ISO formatted creation timestamp.
  - `updatedTimestamp`: ISO formatted update timestamp.

### Example Response
```json
{
  "metadata": {
    "postId": 123,
    "userId": 456,
    "page": 1,
    "count": 10
  },
  "comments": [
    {
      "id": 789,
      "user": {
        "id": 890,
        "username": "user123"
      },
      "text": "Great post!",
      "upvotes": 15,
      "userUpvotes": true,
      "createdTimestamp": "2023-01-01T12:00:00",
      "updatedTimestamp": "2023-01-01T13:00:00"
    },
    // ... more comments ...
  ]
}
```

## Make Comment API

### Description
The Make Comment API allows a user to post a comment on a specific post.

### Request
- **Endpoint**: `POST /makeComment`
- **Body**:
  - `post_id` (int, required): The ID of the post to comment on.
  - `user_id` (int, required): The ID of the user making the comment.
  - `comment_text` (string, required): The text of the comment.

### Example Request
```http
POST /makeComment
Content-Type: application/json

{
  "post_id": 123,
  "user_id": 456,
  "comment_text": "Interesting perspective!"
}
```

### Response
- **message**: Confirmation message.
- **comment_id**: The ID of the newly created comment.

### Example Response
```json
{
  "message": "Comment added successfully",
  "comment_id": 789
}
```

## Upvote Comment API

### Description
The Upvote Comment API allows a user to upvote a comment.

### Request
- **Endpoint**: `PUT /upvoteComment`
- **Body**:
  - `user_id` (int, required): The ID of the user upvoting the comment.
  - `comment_id` (int, required): The ID of the comment being upvoted.

### Example Request
```http
PUT /upvoteComment
Content-Type: application/json

{
  "user_id": 456,
  "comment_id": 789
}
```

### Response
- **message**: Confirmation message.

### Example Response
```json
{
  "message": "Comment upvoted successfully"
}
```

## Remove Upvote Comment API

### Description
The Remove Upvote Comment API allows a user to remove their upvote from a comment.

### Request
- **Endpoint**: `PUT /removeUpvoteComment`
- **Body**:
  - `user_id` (int, required): The ID of the user removing the upvote.
  - `comment_id` (int, required): The ID of the comment from which the upvote is being removed.

### Example Request
```http
PUT /removeUpvoteComment
Content-Type: application/json

{
  "user_id": 456,
  "comment_id": 789
}
```

### Response
- **message**: Confirmation message.

### Example Response
```json
{
  "message": "Comment upvote removed successfully"
}
```
``
## Make Post API

### Description
The Make Post API allows users to create a new post. Users can specify a title, body, and associate the post with multiple categories.

### Request
- **Endpoint**: `POST /makePost`
- **Body**:
  - `user_id` (int, required): The ID of the user creating the post.
  - `title` (string, required): Title of the post.
  - `body` (string, required): Body content of the post.
  - `categories` (array of strings, optional): List of category names to associate with the post.

### Example Request
```json
POST /makePost
{
  "user_id": 123,
  "title": "New Tech Trends",
  "body": "Discussing the latest in technology...",
  "categories": ["Technology", "Innovation"]
}
```

### Response
- On successful creation:
  - Status Code: 201
  - Body: `{ "message": "Post created successfully", "post_id": [newly created post ID] }`

---

## Edit Post API

### Description
The Edit Post API allows users to modify an existing post, including its title, body, and associated categories.

### Request
- **Endpoint**: `PUT /editPost`
- **Body**:
  - `post_id` (int, required): The ID of the post to be edited.
  - `user_id` (int, required): The ID of the user editing the post (for validation).
  - `title` (string, optional): New title of the post.
  - `body` (string, optional): New body content of the post.
  - `categories` (array of strings, optional): Updated list of category names for the post.

### Example Request
```json
PUT /editPost
{
  "post_id": 456,
  "user_id": 123,
  "title": "Updated Tech Trends",
  "body": "An updated discussion on technology...",
  "categories": ["Tech", "Innovation", "Future"]
}
```

### Response
- On successful update:
  - Status Code: 200
  - Body: `{ "message": "Post updated successfully" }`

---

## Upvote Post API

### Description
The Upvote Post API allows users to upvote a post. It prevents multiple upvotes on the same post by the same user.

### Request
- **Endpoint**: `PUT /upvotePost`
- **Body**:
  - `user_id` (int, required): The ID of the user upvoting the post.
  - `post_id` (int, required): The ID of the post being upvoted.

### Example Request
```json
PUT /upvotePost
{
  "user_id": 123,
  "post_id": 456
}
```

### Response
- On successful upvote:
  - Status Code: 200
  - Body: `{ "message": "Post upvoted successfully" }`

---

## Remove Upvote Post API

### Description
The Remove Upvote Post API allows users to retract their upvote from a post.

### Request
- **Endpoint**: `PUT /removeUpvotePost`
- **Body**:
  - `user_id` (int, required): The ID of the user removing the upvote.
  - `post_id` (int, required): The ID of the post from which the upvote is being removed.

### Example Request
```json
PUT /removeUpvotePost
{
  "user_id": 123,
  "post_id": 456
}
```

### Response
- On successful upvote removal:
  - Status Code: 200
  - Body: `{ "message": "Post upvote removed successfully" }`

## Signup API

### Description
The Signup API allows new users to register. It captures essential user information and associates their chosen tech stack with their profile.

### Request
- **Endpoint**: `PUT /signup`
- **Body**:
  - `first_name` (string, required): User's first name.
  - `last_name` (string, optional): User's last name.
  - `username` (string, required): Desired username.
  - `email` (string, required): User's email address.
  - `password` (string, required): User's chosen password.
  - `techstack` (array of strings, optional): List of technology or vendor names associated with the user's tech stack.

### Example Request
```json
PUT /signup
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "securepassword123",
  "techstack": ["Python", "JavaScript"]
}
```

### Response
- On successful signup:
  - Status Code: 201
  - Body: `{ "message": "Signup successful", "user_id": [newly created user ID] }`

---

## Edit Profile API

### Description
The Edit Profile API allows users to update their profile information, including their name, email, password, and tech stack.

### Request
- **Endpoint**: `PUT /editProfile`
- **Body**:
  - `user_id` (int, required): ID of the user whose profile is being edited.
  - `first_name` (string, optional): Updated first name.
  - `last_name` (string, optional): Updated last name.
  - `email` (string, optional): Updated email address.
  - `password` (string, optional): Updated password.
  - `techstack` (array of strings, optional): Updated list of technology or vendor names associated with the user's tech stack.

### Example Request
```json
PUT /editProfile
{
  "user_id": 123,
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "janedoe@example.com",
  "password": "newsecurepassword456",
  "techstack": ["React", "Node.js"]
}
```

### Response
- On successful profile update:
  - Status Code: 200
  - Body: `{ "message": "Profile updated successfully" }`

## Discover Vendors API

### Description
The Discover Vendors API retrieves a list of vendors, paginated.

### Request
- **Endpoint**: `GET /discover`
- **Parameters**:
  - `page` (int, optional): The page number for pagination. Default is 1.
  - `count` (int, optional): Number of records per page. Default is 10.

### Example Request
```
GET /discover?page=2&count=5
```

### Response
- A list of vendors with details including ID, name, description, URL, and timestamps.

---

## Get Vendor API

### Description
The Get Vendor API retrieves detailed information for a specific vendor.

### Request
- **Endpoint**: `GET /getVendor`
- **Parameters**:
  - `vendor_id` (int, required): The ID of the vendor to retrieve.

### Example Request
```
GET /getVendor?vendor_id=123
```

### Response
- On success:
  - Vendor information including ID, name, description, URL, and timestamps.
- On failure (vendor not found or invalid ID):
  - Error message with status code 404.

---

## Add Vendor API

### Description
The Add Vendor API allows for adding a new vendor to the database.

### Request
- **Endpoint**: `POST /addVendor`
- **Body**:
  - `vendor_name` (string, required): Name of the vendor.
  - `descriptio



## License
This project is licensed under the [MIT License](LICENSE).


