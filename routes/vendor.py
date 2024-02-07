from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from db_manager import DBManager

vendor_bp = Blueprint('vendor_bp', __name__)
db_manager = DBManager()

@vendor_bp.route('/discover/categories', methods=['GET'])
def get_discover():

    conn = db_manager.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT id, category_name, description
    FROM DiscoverCategory
    """
    cursor.execute(query)

    discover_categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(discover_categories)

@vendor_bp.route('/discover/items', methods=['GET'])
def get_vendor_category():
    """TODO: Vendor bodies within a particular category"""
    return False

@vendor_bp.route('/getVendor', methods=['GET'])
def get_vendor():
    vendor_id = request.args.get('vendor_id', type=int)

    if not vendor_id:
        return jsonify({"error": "Vendor ID is required"}), 400

    conn = db_manager.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT id, vendor_name, description, vendor_url, creation_time, update_time
    FROM DiscoverVendor
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
            INSERT INTO PublicVendor (vendor_name, description, vendor_url)
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
