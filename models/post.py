# models/user.py
from flask import current_app as app
from typing import Optional, Tuple, List
from werkzeug.exceptions import InternalServerError
import pymysql
import pymysql.cursors
from utils import DBManager

class Post:
    def __init__(self):
        self.db_manager = DBManager()
        self.conn = self.db_manager.get_db_connection()
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __get_category_ids_from_post_id(self, post_id:int) -> List[int]:
        """Returns a list of category ids associated with a post"""
        self.cursor.execute("""SELECT category_id FROM PostDiscussCategory WHERE post_id = %s""", (post_id))
        category_ids = self.cursor.fetchall()
        category_ids = [item['category_id'] for item in category_ids]
        return category_ids

    def __get_vendor_ids_from_post_id(self, post_id:int) -> List[int]:
        """Returns a list of vendor ids associated with a post"""
        self.cursor.execute("""SELECT vendor_id FROM PostDiscussVendor WHERE post_id = %s""", (post_id))
        vendor_ids = self.cursor.fetchall()
        vendor_ids = [item['vendor_id'] for item in vendor_ids]
        return vendor_ids
    
    def __check_user_vote_from_id(self, post_id:int, user_id:int) -> Tuple[Optional[bool], Optional[int]]:
        # Return true for upvote, false for downvote, none for none
        self.cursor.execute("""
            SELECT id, is_downvote FROM PostUpvote 
            WHERE user_id = %s AND post_id = %s
        """, (user_id, post_id))
        vote = self.cursor.fetchone()
        if not vote:
            return None, None
        elif vote.get['is_downvote'] is True:
            return False, vote.get['id']
        else:
            return True, vote.get['id']
    
    def __delete_vote_from_id(self, vote_id:int) -> None:
        self.cursor.execute("""
            DELETE FROM PostUpvote 
            WHERE id = %s
        """, (vote_id,))
    
    def __insert_vote_from_id(self, post_id:int, user_id:int, is_downvote:bool) -> None:
        self.cursor.execute("""
            INSERT INTO PostUpvote (post_id, user_id, is_downvote)
            VALUES (%s, %s, %s)
        """, (post_id, user_id, is_downvote))        

    def toggle_post_vote(self, post_id:int, user_id:int, is_downvote:bool) -> None:
        try:
            user_vote, vote_id = self.__check_user_vote_from_id(post_id, user_id)
            if user_vote is None:
                self.__insert_vote_from_id(post_id, user_id, is_downvote)
            elif user_vote is True:
                if is_downvote:
                # User has upvoted, delete vote object (if is_downvote)
                    self.__delete_vote_from_id(vote_id)
                # Do nothing otherwise
            else:
                if not is_downvote:
                # User has downvoted, delete vote object (if not is_downvote)
                    self.__delete_vote_from_id(post_id, vote_id)
                # Do nothing otherwise
        except pymysql.MySQLError as e:
            app.logger.error(str(e))
            raise InternalServerError(str(e))
        finally:
            self.conn.commit()
            self.conn.close()
            self.cursor.close()

    def create_post_and_fetch_id(
            self,
            author_id:int,
            title:str,
            body:str,
            category_ids:List[int],
            is_anonymous:bool,
            tagged_vendor_ids:List[int]
    )->int:
        try:
            # Insert post into database
            self.cursor.execute("""
                INSERT INTO Post (user_id, title, body, is_anonymous) 
                VALUES (%s, %s, %s, %s)
            """, (author_id, title, body, is_anonymous))
            post_id = self.cursor.lastrowid

            # Link post to categories
            for category_id in category_ids:
                self.cursor.execute("""
                    INSERT INTO PostDiscussCategory (post_id, category_id) 
                    VALUES (%s, %s)
                """, (post_id, category_id))
            
            # Link post to vendors
            for tagged_vendor_id in tagged_vendor_ids:
                self.cursor.execute("""
                    INSERT INTO PostDiscoverVendor(post_id, vendor_id) 
                    VALUES (%s, %s)
                """, (post_id, tagged_vendor_id))
            
            return post_id
            
        except pymysql.MySQLError as e:
            self.conn.rollback()
            app.logger.error(str(e))
            raise InternalServerError(str(e))
    
        finally:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
    
    def edit_post(self,
                author_id:int,
                post_id:int,
                new_title:str = None,
                new_body:str = None,
                new_category_ids:List[int] = None,
                new_vendor_ids:List[int] = None) -> None:
        
        try:
            # Edit post information
            if new_title:
                self.cursor.execute("""
                    UPDATE Post SET title = COALESCE(%s, title),
                                    update_time = CURRENT_TIMESTAMP(3)
                    WHERE id = %s AND user_id = %s
                """, (new_title, post_id, author_id))
                self.title = new_title

            if new_body:
                self.cursor.execute("""
                    UPDATE Post SET body = COALESCE(%s, body),
                                    update_time = CURRENT_TIMESTAMP(3)
                    WHERE id = %s AND user_id = %s
                """, (new_body, self.post_id, self.author_id))
            
            if new_category_ids:
                old_category_ids = self.__get_category_ids_from_post_id(post_id)
                # Add new categories
                for category_id in new_category_ids - old_category_ids:
                        self.cursor.execute("""
                            INSERT INTO PostDiscussCategory (post_id, category_id) 
                            VALUES (%s, %s)
                        """, (self.post_id, category_id))
                
                # Delete old categories (TODO: Efficiency)
                for category_id in old_category_ids - new_category_ids:
                        self.cursor.execute("""
                            DELETE FROM PostDiscussCategory 
                            WHERE post_id = %s AND category_id = %s
                        """, (self.post_id, category_id))

            if new_vendor_ids:
                # Add new vendors (TODO: Efficiency)
                old_tagged_vendor_ids = self.__get_vendor_ids_from_post_id(post_id)
                for vendor_id in new_vendor_ids - old_tagged_vendor_ids:
                        self.cursor.execute("""
                            INSERT INTO PostDiscoverVendor (post_id, vendor_id) 
                            VALUES (%s, %s)
                        """, (post_id, vendor_id))
                
                # Delete old vendors (TODO: Efficiency)
                for vendor_id in old_tagged_vendor_ids - new_vendor_ids:
                        self.cursor.execute("""
                            DELETE FROM PostDiscoverVendor
                            WHERE post_id = %s AND vendor_id = %s
                        """, (post_id, vendor_id))
        except pymysql.MySQLError as e:
            app.logger.error(str(e))
            raise InternalServerError(str(e))
        finally:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()