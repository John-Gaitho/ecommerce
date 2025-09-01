# seed.py
from app import create_app, db
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.cart_item import CartItem
from app.models.order import Order, OrderItem
from app.models.review import Review
from slugify import slugify
from decimal import Decimal

def seed():
    print("Clearing existing data...")
    # Delete in order to avoid foreign key constraints
    db.session.execute("DELETE FROM order_items")
    db.session.execute("DELETE FROM orders")
    db.session.execute("DELETE FROM cart_items")
    db.session.execute("DELETE FROM reviews")
    db.session.execute("DELETE FROM products")
    db.session.execute("DELETE FROM users")
    db.session.commit()

    print("Seeding users...")
    admin = User(email="admin@example.com", name="Admin User", role=UserRole.ADMIN)
    admin.set_password("adminpass")
    customer = User(email="customer@example.com", name="Customer User", role=UserRole.CUSTOMER)
    customer.set_password("customerpass")

    db.session.add_all([admin, customer])
    db.session.commit()

    print("Seeding products...")
    products_data = [
        {"name": "Custom Mug", "description": "White ceramic mug", "category": "cups", "price": 12.99, "stock_quantity": 50},
        {"name": "Travel Mug", "description": "Stainless steel travel mug", "category": "cups", "price": 19.99, "stock_quantity": 30},
        {"name": "Coffee Cup", "description": "Classic coffee cup", "category": "cups", "price": 8.99, "stock_quantity": 40},
    ]
    products = []
    for p in products_data:
        prod = Product(
            name=p["name"],
            description=p["description"],
            category=p["category"],
            price=Decimal(p["price"]),
            stock_quantity=p["stock_quantity"],
            slug=slugify(p["name"]),
        )
        products.append(prod)
        db.session.add(prod)
    db.session.commit()

    print("Seeding cart items...")
    cart_item = CartItem(user_id=customer.id, product_id=products[0].id, quantity=2)
    db.session.add(cart_item)
    db.session.commit()

    print("Seeding orders...")
    order = Order(
        user_id=customer.id,
        total_amount=Decimal('34.97'),
        shipping_address="123 Main St",
        status="pending"
    )
    db.session.add(order)
    db.session.commit()  # flush to get order.id

    order_item = OrderItem(
        order_id=order.id,
        product_id=products[0].id,
        quantity=2,
        price=products[0].price
    )
    db.session.add(order_item)
    db.session.commit()

    print("Seeding reviews...")
    review = Review(
        user_id=customer.id,
        product_id=products[0].id,
        rating=5,
        comment="Great mug!"
    )
    db.session.add(review)
    db.session.commit()

    print("Seeding completed!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
