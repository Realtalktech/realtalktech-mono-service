SET FOREIGN_KEY_CHECKS = 0;  -- Disable foreign key checking to avoid issues with dropping tables

DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Post;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS DiscoverCategory;
DROP TABLE IF EXISTS UserCategory;
DROP TABLE IF EXISTS PostCategory;
DROP TABLE IF EXISTS PublicVendor;
DROP TABLE IF EXISTS UserEndorsement;
DROP TABLE IF EXISTS DiscoverVendor;
DROP TABLE IF EXISTS DiscoverVendorCategory;
DROP TABLE IF EXISTS UserVendor;
DROP TABLE IF EXISTS PostVendor;
DROP TABLE IF EXISTS Comment;
DROP TABLE IF EXISTS CommentTag;
DROP TABLE IF EXISTS PostUpvote;
DROP TABLE IF EXISTS CommentUpvote;

SET FOREIGN_KEY_CHECKS = 1;  -- Re-enable foreign key checking
