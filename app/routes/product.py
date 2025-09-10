# app/routes/products.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.product import Product
from app.utils.decorators import role_required
from flask_jwt_extended import jwt_required

products_bp = Blueprint("products", __name__)

# --- LIST / SEARCH / FILTER / SORT / PAGINATION ---
@products_bp.get("/")
def list_products():
    q = Product.query

    # --- Search ---
    search = request.args.get("q")
    if search:
        q = q.filter(
            Product.name.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )

    # --- Category filter (single or multiple) ---
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

    # --- Price range filter ---
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


# --- GET SINGLE PRODUCT BY SLUG ---
@products_bp.get("/<slug>")
def get_product(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    return jsonify(p.to_dict())


# --- CREATE PRODUCT (ADMIN ONLY) ---
@products_bp.post("/")
@jwt_required()
@role_required("admin")
def create_product():
    data = request.get_json() or {}
    p = Product(
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
    db.session.add(p)
    db.session.commit()
    return jsonify({"message": "created", "id": str(p.id)}), 201


# --- UPDATE PRODUCT (ADMIN ONLY) ---
@products_bp.put("/<slug>")
@jwt_required()
@role_required("admin")
def update_product(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    data = request.get_json() or {}
    for field in ["name", "description", "price", "image_url", "category", "specifications", "stock_quantity", "is_featured"]:
        if field in data:
            setattr(p, field, data[field])
    db.session.commit()
    return jsonify({"message": "updated"})


# --- DELETE PRODUCT (ADMIN ONLY) ---
@products_bp.delete("/<slug>")
@jwt_required()
@role_required("admin")
def delete_product(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "deleted"})
