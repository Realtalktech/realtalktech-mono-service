CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE Post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    description TINYTEXT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE DiscoverCategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    description TINYTEXT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE UserCategory (
    user_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (category_id) REFERENCES Category(id),
    PRIMARY KEY (user_id, category_id)
);

CREATE TABLE PostCategory (
    post_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (category_id) REFERENCES Category(id),
    PRIMARY KEY (post_id, category_id)
);

CREATE TABLE PublicVendor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE DiscoverVendor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(255) UNIQUE NOT NULL,
    vendor_type VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    vendor_hq VARCHAR(255),
    total_offices INT,
    local_employees INT,
    total_employees INT,
    vendor_homepage_url VARCHAR(255),
    vendor_logo_url VARCHAR(255),
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE DiscoverVendorCategory (
    vendor_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (vendor_id) REFERENCES DiscoverVendor(id),
    FOREIGN KEY (category_id) REFERENCES DiscoverCategory(id),
    PRIMARY KEY (vendor_id, category_id)
);

CREATE TABLE UserVendor (
    user_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (vendor_id) REFERENCES PublicVendor(id),
    PRIMARY KEY (user_id, vendor_id)
);

CREATE TABLE PostVendor (
    post_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (vendor_id) REFERENCES DiscoverVendor(id),
    PRIMARY KEY (post_id, vendor_id)
);

CREATE TABLE Comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    user_id INT,
    comment_text TEXT NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE CommentTag (
    comment_id INT,
    tagged_user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (comment_id) REFERENCES Comment(id),
    FOREIGN KEY (tagged_user_id) REFERENCES User(id),
    PRIMARY KEY (comment_id, tagged_user_id)
);

CREATE TABLE PostUpvote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE CommentUpvote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT,
    user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (comment_id) REFERENCES Comment(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);
