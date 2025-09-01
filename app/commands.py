# app/commands.py
import click
from flask.cli import with_appcontext
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.user_roles import UserRole
import uuid


@click.command("create-admin")
@with_appcontext
def create_admin():
    """Create an initial admin user."""
    email = click.prompt("Enter admin email", type=str)
    password = click.prompt("Enter admin password", type=str, hide_input=True, confirmation_prompt=True)

    # Check if already exists
    if User.query.filter_by(email=email).first():
        click.echo("❌ User with this email already exists.")
        return

    # Create user
    new_user = User(
        id=uuid.uuid4(),
        name="Admin",
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add(new_user)
    db.session.commit()

    # Assign admin role
    role = UserRole(user_id=new_user.id, role="admin")
    db.session.add(role)
    db.session.commit()

    click.echo(f"✅ Admin created: {email}")
