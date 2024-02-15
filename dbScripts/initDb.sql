SELECT 'Spinning up RTT Tables....' as '';

CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    current_company VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    linkedin_url VARCHAR(255),
    bio VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE Post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    is_anonymous BOOLEAN NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE DiscussCategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    description TINYTEXT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE DiscoverCategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE InterestArea (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interest_area_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE Industry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    industry_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)    
);

CREATE TABLE UserIndustry(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    industry_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (industry_id) REFERENCES Industry(id)    
);

CREATE TABLE UserInterestArea (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    interest_area_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (interest_area_id) REFERENCES InterestArea(id)
);

CREATE TABLE UserDiscussCategory (
    user_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (category_id) REFERENCES DiscussCategory(id),
    PRIMARY KEY (user_id, category_id)
);

CREATE TABLE PostDiscussCategory (
    post_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (category_id) REFERENCES DiscussCategory(id),
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
    total_employees INT,
    vendor_homepage_url VARCHAR(255),
    vendor_logo_url VARCHAR(255),
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE UserPublicVendorEndorsement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endorser_user_id INT,
    endorsee_user_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (vendor_id) REFERENCES PublicVendor(id),
    FOREIGN KEY (endorser_user_id) REFERENCES User(id),
    FOREIGN KEY (endorsee_user_id) REFERENCES User(id)
);

CREATE TABLE VendorDiscoverCategory (
    vendor_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (vendor_id) REFERENCES DiscoverVendor(id),
    FOREIGN KEY (category_id) REFERENCES DiscoverCategory(id),
    PRIMARY KEY (vendor_id, category_id)
);

CREATE TABLE UserPublicVendor (
    user_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (vendor_id) REFERENCES PublicVendor(id),
    PRIMARY KEY (user_id, vendor_id)
);

CREATE TABLE PostDiscoverVendor (
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT,
    tagged_user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (comment_id) REFERENCES Comment(id),
    FOREIGN KEY (tagged_user_id) REFERENCES User(id)
);

CREATE TABLE PostUpvote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    user_id INT,
    is_downvote BOOLEAN NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE CommentUpvote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT,
    user_id INT,
    is_downvote BOOLEAN NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (comment_id) REFERENCES Comment(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

SELECT 'Warnings' as 'Initial DB Table Setup Complete.';
SHOW WARNINGS;