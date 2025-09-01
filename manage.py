import click
from flask.cli import with_appcontext
from app.extensions import db
from app import create_app
from app.models import *  # import models so tables are registered

app = create_app()

@app.cli.command("create_db")
@with_appcontext
def create_db():
    """Create all database tables."""
    db.create_all()
    click.echo("Database tables created.")

@app.cli.command("drop_db")
@with_appcontext
def drop_db():
    """Drop all database tables."""
    db.drop_all()
    click.echo("Database tables dropped.")

@app.cli.command("seed")
@with_appcontext
def seed():
    """Seed the database with sample data."""
    # Example seed data
    from app.models.product import Product
    sample = Product(
        name="Test Cup",
        slug="test-cup",
        price=9.99,
        stock_quantity=100
    )
    db.session.add(sample)
    db.session.commit()
    click.echo("Database seeded with sample data.")
