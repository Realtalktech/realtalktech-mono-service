SHOW TABLES;

DESCRIBE User;
DESCRIBE Post;
DESCRIBE Comment;
DESCRIBE CommentTag;
DESCRIBE CommentUpvote;
DESCRIBE PostUpvote;
DESCRIBE Category;

-- Sample query to check ENUM type for CategoryName
SELECT column_type 
FROM information_schema.COLUMNS 
WHERE TABLE_NAME = 'Category' AND COLUMN_NAME = 'name';
