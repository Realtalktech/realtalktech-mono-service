SET FOREIGN_KEY_CHECKS = 0;  -- Disable foreign key checking to avoid issues with dropping tables

DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Post;
DROP TABLE IF EXISTS DiscussCategory;
DROP TABLE IF EXISTS DiscoverCategory;
DROP TABLE IF EXISTS UserDiscussCategory;
DROP TABLE IF EXISTS PostDiscussCategory;
DROP TABLE IF EXISTS PublicVendor;
DROP TABLE IF EXISTS UserPublicVendorEndorsement;
DROP TABLE IF EXISTS DiscoverVendor;
DROP TABLE IF EXISTS VendorDiscoverCategory;
DROP TABLE IF EXISTS UserPublicVendor;
DROP TABLE IF EXISTS PostDiscoverVendor;
DROP TABLE IF EXISTS InterestArea;
DROP TABLE IF EXISTS UserInterestArea;
DROP TABLE IF EXISTS Industry;
DROP TABLE IF EXISTS UserIndustry;
DROP TABLE IF EXISTS Comment;
DROP TABLE IF EXISTS CommentTag;
DROP TABLE IF EXISTS PostUpvote;
DROP TABLE IF EXISTS CommentUpvote;

SET FOREIGN_KEY_CHECKS = 1;  -- Re-enable foreign key checking
