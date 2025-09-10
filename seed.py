import random
from faker import Faker
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Profile, Product, Review, Order, OrderItem, CartItem
from app.extensions import bcrypt

fake = Faker()
app = create_app()


def reset_database():
    print("🧹 Resetting database...")
    db.drop_all()
    db.create_all()


def seed_users():
    print("👤 Seeding users...")

    # ✅ Real admin user
    admin = User(
        email="admin@example.com",
        password_hash=bcrypt.generate_password_hash("adminpassword").decode('utf-8'),
        name="Admin User",
        role="ADMIN",
    )
    db.session.add(admin)

    users = [admin]

    # ✅ Other customers
    for i in range(5):
        user = User(
            email=f"user{i}@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
            name=fake.name(),
            role="CUSTOMER",
        )
        users.append(user)
        db.session.add(user)

    db.session.commit()
    print(f"✅ Seeded {len(users)} users")
    return [u.id for u in users]

def seed_profiles(user_ids):
    print("👤 Seeding profiles...")
    for uid in user_ids:
        profile = Profile(
            user_id=uid,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            address=fake.address(),
            phone_number=fake.phone_number(),
        )
        db.session.add(profile)
    db.session.commit()
    print(f"✅ Seeded {len(user_ids)} profiles")


def seed_products():
    print("📦 Seeding products...")
    products = [
        Product(
            name="Classic Ceramic Mug",
            description="A sturdy ceramic mug for everyday use.",
            image_url="https://m.media-amazon.com/images/I/612vRQpWJyL.jpg",
            slug="classic-ceramic-mug",
            category="cups",
            price=9.99,
            stock_quantity=100,
            is_featured=True,
            specifications={"color": "white", "material": "ceramic"},
        ),
        Product(
            name="Travel Mug",
            description="Insulated travel mug to keep drinks hot or cold.",
            image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQF9R99sVHZh809Jw5-_y7KxKUJ2KQaXhv6eSWpWetBz8TYL0dWPhMqJHkUTzy5T1y7aeY&usqp=CAU",
            slug="travel-mug",
            category="cups",
            price=14.99,
            stock_quantity=50,
            is_featured=False,
            specifications={"color": "black", "material": "stainless steel"},
        ),
        Product(
            name="Custom Photo Mug",
            description="Personalize your mug with a custom photo print.",
            image_url="https://m.media-amazon.com/images/I/61jGZ+8nJDL._AC_SL1500_.jpg",
            slug="custom-photo-mug",
            category="cups",
            price=12.99,
            stock_quantity=75,
            is_featured=True,
            specifications={"color": "white", "material": "ceramic"},
        ),
    ]

    db.session.add_all(products)
    db.session.commit()
    print(f"✅ Seeded {len(products)} products")
    return [p.id for p in products]


def seed_reviews(user_ids, product_ids):
    print("⭐ Seeding reviews...")
    for _ in range(10):
        review = Review(
            rating=random.randint(3, 5),
            comment=fake.sentence(),
            user_id=random.choice(user_ids),
            product_id=random.choice(product_ids),
        )
        db.session.add(review)
    db.session.commit()
    print("✅ Seeded reviews")


def seed_orders(user_ids, product_ids):
    print("🛒 Seeding orders...")
    for uid in user_ids:
        num_orders = random.randint(1, 2)
        for _ in range(num_orders):
            order = Order(
                user_id=uid,
                status=fake.random_element(["pending", "shipped", "delivered"]),
                total_price=0.0  # will calculate after adding items
            )
            db.session.add(order)
            db.session.flush()  # ensures order.id is available for items

            order_total = 0.0
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                product_id = random.choice(product_ids)
                product = db.session.get(Product, product_id)
                if not product:
                    continue
                quantity = random.randint(1, 5)
                price = float(product.price)

                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=price
                )
                db.session.add(item)
                order_total += price * quantity

            order.total_price = order_total

    db.session.commit()
    print("✅ Seeded orders")

def seed_cart_items(user_ids, product_ids):
    print("🛍️ Seeding cart items...")
    for uid in user_ids:
        for _ in range(random.randint(1, 3)):
            cart_item = CartItem(
                user_id=uid,
                product_id=random.choice(product_ids),
                quantity=random.randint(1, 5),
            )
            db.session.add(cart_item)
    db.session.commit()
    print("✅ Seeded cart items")


if __name__ == "__main__":
    with app.app_context():
        reset_database()
        user_ids = seed_users()
        seed_profiles(user_ids)
        product_ids = seed_products()
        seed_reviews(user_ids, product_ids)
        seed_orders(user_ids, product_ids)
        seed_cart_items(user_ids, product_ids)
        print("🎉 Database seeding complete!")
