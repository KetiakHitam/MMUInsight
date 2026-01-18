import click
import os
from app import app, db
from models import User
from extensions import bcrypt

@app.cli.command()
def create_default_accounts():
    """Create admin/owner accounts from environment variables"""
    with app.app_context():
        admin_pass = os.environ.get('ADMIN_PASSWORD')
        owner_pass = os.environ.get('OWNER_PASSWORD')
        
        if not admin_pass or not owner_pass:
            click.echo("ERROR: ADMIN_PASSWORD and OWNER_PASSWORD env vars not set")
            return
        
        accounts = [
            ("admin@mmu.edu.my", "ADMIN", admin_pass),
            ("owner@mmu.edu.my", "OWNER", owner_pass),
        ]
        
        for email, role, password in accounts:
            if User.query.filter_by(email=email).first():
                click.echo(f"✓ {email} already exists")
                continue
            
            user = User(
                email=email,
                user_type="lecturer",
                role=role,
                is_verified=True,
                is_claimed=True
            )
            user.password_hash = bcrypt.generate_password_hash(password)
            db.session.add(user)
            db.session.commit()
            click.echo(f"✓ Created {role}: {email}")
