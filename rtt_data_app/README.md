# Real Talk - Database Overview

This document is an overview of the Real Talk platform's database schemas and organization. RealTalk's DB Cluster currently runs on the MySQL 8.0 engine. It uses SQLite with an identical schema (adjusted for data type constraints) for unit testing. Last updated 3/26/24

## Table of Contents

- [Root Tables](#root-tables)
    - [User](#user)
    - [Post](#post)
    - [Comment](#comment)
    - [Discover Vendor](#discover-vendor)
    - [Public Vendor](#public-vendor)
    - [Discuss Category](#discuss-category)
    - [Discover Category](#discover-category)
    - [Interest Area](#interest-area)
    - [Industry](#industry)
- [User Join Tables](#user-join-tables)
    - [User Industry](#user-industry)
    - [User Interest Area](#user-interest-area)
    - [User Discuss Category](#user-discuss-category)
    - [User Public Vendor](#user-public-vendor)
    - [User Public Vendor Endorsement](#user-public-vendor-endorsement)
- [Post Join Tables](#post-join-tables)
    - [Post Discuss Category](#post-discuss-category)
    - [Post Discover Vendor](#post-discover-vendor)
    - [Post Upvote](#post-upvote)
- [Comment Join Tables](#comment-join-tables)
    - [Comment Tag](#comment-tag)
    - [Comment Upvote](#comment-upvote)
- [Vendor Join Tables](#vendor-join-tables)
    - [VendorDiscoverCategory](#vendor-discover-category)
- [License](#license)

## Root Tables

The section below describes the "root" tables contained in the RTT database cluster. These are the tables that serve to describe core elements, with associated join tables for various features described in later sections.

### User
```sql
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
```
id - A user's unique account id
full_name - A user's full name, required
username - A user's unique username, required
current_company - A user's current place of work, required
email - A user's unique email, required
linkedin_url - A user's linkedin, not required
password - A user's account password, hashed before insertion
creation_time/update_time - Account creation and update times, respectively. Returned in ISO format

### Post
```sql
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
```
id - A post's unique id
user_id - Foreign key, the id of the user who authored the post
is_anonymous - Boolean of whether post was created anonymously, required
title - Post title, required
body - Post body, required
creation_time - Post creation time, returned in ISO format
update_time - Post update time, returned in ISO format


### Comment
```sql
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
```
id - A comment's unique id
post_id - The id of the post the comment was left under, foreign key
user_id - The id of the user who authored the comment, foreign key
comment_text - The body of the comment, enforced not null
creation/update_time - Self explanatory


### Discover Vendor
```sql
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
```

This table details all vendors that are listed on the "Discover" section. This is unique from a "public vendor" which is detailed below. Essentially, this table includes all vendors that have the ability to "claim" a profile down the road.

id - A vendor's unique id
vendor_name - The name of the vendor
vendor_type - TODO: Will be removed in lieu of a marketplace join table
description - A description of the company's business/offerings
vendor_hq - The location of the vendor's HQ
total_employees - The number of employees a vendor has, rounded down to the nearest 1000
vendor_homepage_url - A link to the vendor's pricing page
vendor_logo_url - A link to an S3 object store filepath to the vendor's logo
creation/update_time - Self explanatory

### Public Vendor
```sql
CREATE TABLE PublicVendor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    discover_vendor_id INT NULL,  -- Nullable foreign key referencing DiscoverVendor
    vendor_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (discover_vendor_id) REFERENCES DiscoverVendor(id)  -- Foreign key constraint
);
```
The public vendor table will be initially populated with the same data as "DiscoverVendor" the difference here is in usage. As mentioned, the DiscoverVendor table contains all vendors with a "claimable" profile down the road. This means DiscoverVendor, as described below, is used for join operations across posts to create a vendor's profile. 

A public vendor, on the other hand, is used for a user's tech stack. A tech stack is the collection of vendors/softwares that a user indicates they are proficient in. DiscoverVendor is an immutable list (for a normal user) whereas PublicVendor has API support for user's to add a vendor or product they don't see yet. This happens upon profile creation or edits. 

id - A vendor's unique id
discover_vendor_id - A nullable FK to reference DiscoverVendor, this allows for flexibility in insights
vendor_name - A public vendor's name
creation/update_time - Self explanatory

### Discuss Category
```sql
CREATE TABLE DiscussCategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    description TINYTEXT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);
```
This table contains all categories that are used for the discuss section of the web app. Its values will generally stay the same over time, but this allows CRUD operations later to update them if needed.

id - A category's unique id, used to join a post with a particular category
category_name - A unique category name
description - The category's description, not enforced
creation/update_time - Self explanatory. 

### Discover Category
```sql
CREATE TABLE DiscoverCategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    icon TEXT NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);
```
Similar to the discuss category table above, this table contains all categories that vendors can be listed under. 

id - A category's unique id, used to join a post with a particular category
category_name - A unique category name
icon - An SVG file, expressed as text, corresponding to the logo of a particular category
creation/update_time - Self explanatory. 

### Interest Area
```sql
CREATE TABLE InterestArea (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interest_area_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)
);
```

This table contains interest areas that a user can specify upon account creation. It will later be used to populate customized marketplace feeds.

id - An interest area's unique id
interest_area_name - The name of the interest area
creation/update_time - Self explanatory

### Industry
```sql
CREATE TABLE Industry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    industry_name VARCHAR(255) UNIQUE NOT NULL,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3)    
);
```

This table contains industries a user can select from when onboarding. It is the answer to the question "what industry do you work in?"

id - An industry's unique id
industry_name - Industry name
creation/update_time - Self explanatory 

## User Join Tables
This section details all tables that attribute various other root tables to a user's profile.

### User Industry
```sql
CREATE TABLE UserIndustry(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    industry_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (industry_id) REFERENCES Industry(id)    
);
```

This table joins an entry from the Industry table to a user's account. 

id - TODO: Remove for clarity. Currently the unique identifier of a given association
user_id - FK referencing a user's id
industry_id - FK referencing an industry's id
creation/update_time - Self explanatory

### User Interest Area
```sql
CREATE TABLE UserInterestArea (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    interest_area_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (interest_area_id) REFERENCES InterestArea(id)
);
```
This table joins an entry from the InterestArea table to a user's account. This will eventually be used for curation purposes.

id - TODO: Remove for clarity. Currently the unique identifier of a given association
user_id - FK referencing a user's id
interest_area_id - FK referencing an interest area's id
creation/update_time - Self explanatory

### User Discuss Category
```sql
CREATE TABLE UserDiscussCategory (
    user_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (category_id) REFERENCES DiscussCategory(id),
    PRIMARY KEY (user_id, category_id)
);
```
This table joins an entry from the DiscussCategory table to a user's account. During onboarding, users are asked "What do you do for work?". The options available are the categories used in the feed for discuss. A user can select 0 or more. Their feed in the discuss "home" category will only contain posts from the categories they've selected during onboarding, or all posts in chronological order, by default.

user_id - FK referencing a user's id
category_id - FK referencing a discuss category's id
creation/update_time - Self explanatory

### User Public Vendor
```sql
CREATE TABLE UserPublicVendor (
    user_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (vendor_id) REFERENCES PublicVendor(id),
    PRIMARY KEY (user_id, vendor_id)
);
```
This table joins an entry from the PublicVendor table to a user's account. This is better known as their "tech stack" which is a list of companies the user claims they have experience in. This is bolstered by an endorsement feature. Similar to LinkedIn, a user can endorse another in a particular skill, or in this case, vendor/software.

user_id - FK referencing a user's id
vendor_id - FK referencing a public vendor's id
creation/update_time - Self explanatory

### User Public Vendor Endorsement
```sql
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
```
As mentioned, user's can endorse one another in their claimed tech stack skills. This table creates an instance of that endorsement and attributes it to the respective users and public vendors. This can be indexed to:
    - Tally the total number of endorsements a user has in a particular skill
        - Track who has endorsed a given user
    - Track the endorsements a user has given to other users
    - Track the number of endorsements a particular vendor has received, overall
        - Track metrics around those endorsement, in conjunction with user data 

id - TODO: Remove for clarity. The unique id of the endorsement instance
endorser_user_id - FK referencing the user id of the user who endorsed another
endorsee_user_id - FK referencing the user id of the user who received an endorsement
vendor_id - FK referencing a public vendor's id
creation/update_time - Self explanatory

## Post Join Tables
This section details all tables that attribute various other root tables to a post.

### Post Discuss Category
```sql
CREATE TABLE PostDiscussCategory (
    post_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (category_id) REFERENCES DiscussCategory(id),
    PRIMARY KEY (post_id, category_id)
);
```
This table joins a post with the category it is in.

post_id - An FK referencing the id of the post
category_id - An FK referencing the discuss category the post is under
creation/update_time - Self explanatory

### Post Discover Vendor
```sql
CREATE TABLE PostDiscoverVendor (
    post_id INT,
    vendor_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (vendor_id) REFERENCES DiscoverVendor(id),
    PRIMARY KEY (post_id, vendor_id)
);
```
Users are able to tag different vendors in a post they create. As a rule of thumb, this generally dictates that the body of the post is pertinent to the tagged vendor. As such, this will be used to populate a discover vendor's profile to display threads where user's have mentioned them. Additional functionality will be built to allow vendors, upon claiming their paid profile, to select the threads they feel best represent their firm.

This means posts can only tag vendors in the DiscoverVendor table. PublicVendors are not an option to tag a post with.

post_id - An FK referencing the id of the post
vendor_id - An FK referencing the DiscoverVendor that the post has tagged
creation/update_time - Self explanatory

### Post Upvote
```sql
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
```
This table tracks the votes that have been submitted for a particular post. It is used to track individual votes, tally individual up/downvote counts, and tally the net number of votes.

post_id - An FK referencing the id of the post
user_id - An FK referencing the id of the user who issued the vote
is_downvote - A boolean. If true, indicates the vote object is a downvote.
creation/update_time - Self explanatory

## Comment Join Tables
This section details all tables that attribute various other root tables to a comment.

### Comment Tag
```sql
CREATE TABLE CommentTag (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT,
    tagged_user_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (comment_id) REFERENCES Comment(id),
    FOREIGN KEY (tagged_user_id) REFERENCES User(id)
);
```
In comments, users are currently able to reply to previous ones by tagging other users in the comment thread. This table attributes a tag to a particular comment. It will be used to populate a corresponding notification, and highlight present tags when a comment is rendered to the web app. 

Currently, the web app will not consider a tag to be valid unless it pertains to a user who is already present in the comment thread. The ability to tag any user is TBD.

comment_id - An FK referencing the id of the comment
tagged_user_id - An FK referecing the id of the user who was tagged
creation/update_time - Self explanatory

### Comment Upvote
```sql
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
```
Similar to PostUpvote, this table tracks the votes that have been submitted for a particular comment. It is used to track individual votes, tally individual up/downvote counts, and tally the net number of votes.

comment_id - An FK referencing the id of the comment
user_id - An FK referencing the id of the user who issued the vote
is_downvote - A boolean. If true, indicates the vote object is a downvote.
creation/update_time - Self explanatory


## Vendor Join Tables
This section details all tables that attribute various other root tables to a vendor.

### Vendor Discover Category
```sql
CREATE TABLE PostDiscussCategory (
    post_id INT,
    category_id INT,
    creation_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    update_time DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    FOREIGN KEY (post_id) REFERENCES Post(id),
    FOREIGN KEY (category_id) REFERENCES DiscussCategory(id),
    PRIMARY KEY (post_id, category_id)
);
```
This table joins a DiscoverVendor, that is, only the vendors present on the discover page, with the category it is in.

post_id - An FK referencing the id of the DiscoverVendor
category_id - An FK referencing the discover category the vendor is under
creation/update_time - Self explanatory

## License

Information about the project's license. State the type of license and link to the LICENSE file.

This project is licensed under the [MIT License](LICENSE).
