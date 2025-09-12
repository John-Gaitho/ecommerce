# app/routes/products.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.product import Product
from app.utils.decorators import role_required
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

products_bp = Blueprint("products", __name__)

# --- LIST / SEARCH / FILTER / SORT / PAGINATION ---
@products_bp.get("/")
def list_products():
    try:
        q = Product.query

        # --- Search ---
        search = request.args.get("q")
        if search:
            q = q.filter(
                Product.name.ilike(f"%{search}%") |
                Product.description.ilike(f"%{search}%")
            )

        # --- Category filter ---
        category = request.args.get("category")
        if category and category != "all":
            categories = [c.strip() for c in category.split(",") if c.strip()]
            if categories:
                q = q.filter(Product.category.in_(categories))

        # --- Featured filter ---
        featured = request.args.get("featured")
        if featured is not None:
            if featured.lower() == "true":
                q = q.filter(Product.is_featured.is_(True))
            elif featured.lower() == "false":
                q = q.filter(Product.is_featured.is_(False))

        # --- In-stock filter ---
        in_stock = request.args.get("in_stock")
        if in_stock and in_stock.lower() == "true":
            q = q.filter(Product.stock_quantity > 0)

        # --- Price range ---
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)
        if min_price is not None:
            q = q.filter(Product.price >= min_price)
        if max_price is not None:
            q = q.filter(Product.price <= max_price)

        # --- Sorting ---
        sort = request.args.get("sort", "created_at")
        order = request.args.get("order", "desc")
        if hasattr(Product, sort):
            sort_column = getattr(Product, sort)
            sort_column = sort_column.desc() if order == "desc" else sort_column.asc()
            q = q.order_by(sort_column)
        else:
            q = q.order_by(Product.created_at.desc())

        # --- Pagination ---
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 12))
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "products": [p.to_dict() for p in pagination.items],
            "pages": pagination.pages,
            "current_page": pagination.page,
            "total": pagination.total
        })
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# --- GET SINGLE PRODUCT BY SLUG ---
@products_bp.get("/<slug>")
def get_product(slug):
    try:
        product = Product.query.filter_by(slug=slug).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# --- CREATE PRODUCT (ADMIN ONLY) ---
@products_bp.post("/")
@jwt_required()
@role_required("admin")
def create_product():
    try:
        data = request.get_json() or {}
        required_fields = ["name", "price", "slug"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            image_url=data.get("image_url"),
            slug=data["slug"],
            category=data.get("category", "cups"),
            specifications=data.get("specifications", {}),
            stock_quantity=data.get("stock_quantity", 0),
            is_featured=data.get("is_featured", False),
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product created", "id": str(product.id)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# --- UPDATE PRODUCT (ADMIN ONLY) ---
@products_bp.put("/<slug>")
@jwt_required()
@role_required("admin")
def update_product(slug):
    try:
        product = Product.query.filter_by(slug=slug).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404

        data = request.get_json() or {}
        for field in ["name", "description", "price", "image_url", "category", "specifications", "stock_quantity", "is_featured"]:
            if field in data:
                setattr(product, field, data[field])

        db.session.commit()
        return jsonify({"message": "Product updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# --- DELETE PRODUCT (ADMIN ONLY) ---
@products_bp.delete("/<slug>")
@jwt_required()
@role_required("admin")
def delete_product(slug):
    try:
        product = Product.query.filter_by(slug=slug).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete product because it is referenced in orders, cart, or reviews"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
