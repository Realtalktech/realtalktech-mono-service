from flask import Blueprint, jsonify, request
from rtt_data_app.app import db
from rtt_data_app.models import DiscoverCategory, DiscoverVendor, VendorDiscoverCategory
import pymysql
import pymysql.cursors
from rtt_data_app.utils import DBManager
from rtt_data_app.auth import token_required
from rtt_data_app.utils.deprecated.responseFormatter import convert_keys_to_camel_case
from werkzeug.exceptions import NotFound, InternalServerError, Unauthorized
import logging
from sqlalchemy import exc, func

vendor_bp = Blueprint('vendor_bp', __name__)
db_manager = DBManager()

logger = logging.getLogger(__name__)

@vendor_bp.route('/discover/groups', methods=['GET'])
@token_required
def get_discover(user_id):
    if not user_id:
        raise Unauthorized
    
    discover_categories = DiscoverCategory.query.all()
    response = []

    for category in discover_categories:
        obj = {
            'id': category.id,
            'name': category.category_name,
            'icon': category.icon
        }
        response.append(obj)

    return jsonify(response)

@vendor_bp.route('/group/<int:discover_category_id>', methods=['GET'])
@token_required
def get_vendors_in_category(user_id, discover_category_id):
    """Get vendor bodies within a particular category"""
    if not user_id:
        raise Unauthorized
    
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    try:
        group = DiscoverCategory.query.filter_by(id=discover_category_id).first()
        id = group.id
        
    except AttributeError as e:
        logger.error(str(e))
        raise NotFound("Discover group not found")

    try:
        # Perform the query using SQLAlchemy
        vendors_query = db.session.query(
            DiscoverVendor.id,
            DiscoverVendor.vendor_name,
            DiscoverVendor.vendor_type,
            DiscoverVendor.description,
            DiscoverVendor.vendor_homepage_url,
            DiscoverVendor.vendor_logo_url
        ).join(
            VendorDiscoverCategory,
            DiscoverVendor.id == VendorDiscoverCategory.vendor_id
        ).filter(
            VendorDiscoverCategory.category_id == discover_category_id
        ).order_by(
            DiscoverVendor.id.desc(),
            DiscoverVendor.creation_time.desc()
        ).paginate(page=page, per_page=count, error_out=False)

        vendors = [
            {
                "id": vendor.id,
                "vendorName": vendor.vendor_name,
                "vendorType": vendor.vendor_type,
                "description": vendor.description,
                "vendorHomepageUrl": vendor.vendor_homepage_url,
                "vendorLogoUrl": vendor.vendor_logo_url
            } for vendor in vendors_query.items
        ]

        metadata = {
            'discoverCategoryId': discover_category_id,
            'page': page,
            'count': count,
            'totalPages': vendors_query.pages,
            'totalItems': vendors_query.total
        }

        return jsonify({"metadata": metadata, "vendors": vendors})
    

    except exc.SQLAlchemyError as e:
        logger.error(str(e))
        raise InternalServerError("An error occured while fetching discover groups.")


@vendor_bp.route('/vendors/<vendor_id>', methods=['GET'])
@token_required
def get_vendor(user_id, vendor_id):
    """Get details for a particular vendor"""
    try:
        if not user_id:
            raise Unauthorized
        
        vendor:DiscoverVendor = DiscoverVendor.query.filter_by(id=vendor_id).first()
        response = {
            'id': vendor.id,
            'name': vendor.vendor_name,
            'description': vendor.description,
            'hq': vendor.vendor_hq,
            'totalEmployees': vendor.total_employees,
            'homepageUrl': vendor.vendor_homepage_url,
            'logoUrl': vendor.vendor_logo_url,
        }
        return response
    except AttributeError as e:
        logger.error(str(e))
        raise NotFound("Vendor not found")
    except exc.SQLAlchemyError as e:
        logger.error(str(e))
        raise InternalServerError("An error occured while fetching a vendor.")

