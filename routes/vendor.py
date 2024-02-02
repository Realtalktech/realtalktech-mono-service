from flask import Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import pymysql
import pymysql.cursors
from db_manager import DBManager
from trie import TrieNode, Trie

vendor_bp = Blueprint('vendor_bp', __name__)
db_manager = DBManager()

trie = Trie()

def update_trie():
    """TODO: Pending DB Changes"""
    return False

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_trie, trigger="interval", hours=1) # Update every hour
scheduler.start()

@vendor_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    prefix = request.args.get('prefix', '')
    suggestions = trie.get_suggestions(prefix)
    return jsonify(suggestions)

@vendor_bp.route('/discover', methods=['GET'])
def get_vendors():
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = db_manager.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT id, vendor_name, description, vendor_url, creation_time, update_time
    FROM Vendor
    ORDER BY id
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, (count, (page - 1) * count))

    vendors = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(vendors)

@vendor_bp.route('/getVendor', methods=['GET'])
def get_vendor():
    vendor_id = request.args.get('vendor_id', type=int)

    if not vendor_id:
        return jsonify({"error": "Vendor ID is required"}), 400

    conn = db_manager.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT id, vendor_name, description, vendor_url, creation_time, update_time
    FROM Vendor
    WHERE id = %s
    """
    cursor.execute(query, (vendor_id,))

    vendor = cursor.fetchone()

    cursor.close()
    conn.close()

    if vendor:
        return jsonify(vendor)
    else:
        return jsonify({"error": "Vendor not found"}), 404
    
@vendor_bp.route('/addVendor', methods=['POST'])
def add_vendor():
    try:
        data = request.json
        vendor_name = data.get('vendor_name')
        description = data.get('description')
        vendor_url = data.get('vendor_url')

        if not vendor_name:
            return jsonify({"error": "Vendor name is required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Insert new vendor into the Vendor table
        cursor.execute("""
            INSERT INTO Vendor (vendor_name, description, vendor_url)
            VALUES (%s, %s, %s)
        """, (vendor_name, description, vendor_url))
        vendor_id = cursor.lastrowid

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Vendor added successfully", "vendor_id": vendor_id}), 201

@vendor_bp.route('/updateVendor', methods=['PUT'])
def update_vendor():
    try:
        data = request.json
        vendor_id = data.get('vendor_id')
        new_vendor_name = data.get('vendor_name')
        new_description = data.get('description')
        new_vendor_url = data.get('vendor_url')

        if not vendor_id:
            return jsonify({"error": "Vendor ID is required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Update vendor details in the Vendor table
        cursor.execute("""
            UPDATE Vendor 
            SET vendor_name = COALESCE(%s, vendor_name), 
                description = COALESCE(%s, description),
                vendor_url = COALESCE(%s, vendor_url)
            WHERE id = %s
        """, (new_vendor_name, new_description, new_vendor_url, vendor_id))

        # Check if the update operation was successful
        if cursor.rowcount == 0:
            return jsonify({"error": "Vendor not found or no new data provided"}), 404

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Vendor updated successfully"}), 200
