CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    userName VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE Post (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    body TEXT,
    creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE
);

CREATE TABLE PostCategory (
    post_id INT,
    category_id INT,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id),
    PRIMARY KEY (post_id, category_id)
);

CREATE TABLE TechStack (
    tech_id INT AUTO_INCREMENT PRIMARY KEY,
    tech_name VARCHAR(255) UNIQUE
);

CREATE TABLE UserTechStack (
    user_id INT,
    tech_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (tech_id) REFERENCES TechStack(tech_id),
    PRIMARY KEY (user_id, tech_id)
);

CREATE TABLE Comment (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    user_id INT,
    comment_text TEXT,
    creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE CommentTags (
    comment_id INT,
    tagged_user_id INT,
    FOREIGN KEY (comment_id) REFERENCES Comments(comment_id),
    FOREIGN KEY (tagged_user_id) REFERENCES User(id),
    PRIMARY KEY (comment_id, tagged_user_id)
);

CREATE TABLE PostUpvotes (
    upvote_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    user_id INT,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE CommentUpvote (
    upvote_id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT,
    user_id INT,
    FOREIGN KEY (comment_id) REFERENCES Comments(comment_id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);
