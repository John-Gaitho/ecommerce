from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, jwt, cors, bcrypt

from .models import *  # noqa

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)



    # Blueprints
    from .routes.auth import auth_bp
    from .routes.product import products_bp
    from .routes.cart import cart_bp
    from .routes.orders import orders_bp
    from .routes.order_item import order_items_bp
    from .routes.reviews import reviews_bp
    from .routes.contact import contact_bp
    from .routes.mpesa import mpesa_bp
    from .routes.profile import profile_bp

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(order_items_bp, url_prefix="/api/order-items")
    app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")
    app.register_blueprint(mpesa_bp, url_prefix="/api/mpesa")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")

    # Health check route
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200
    
     # ✅ Serve uploaded files
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)


    return app
