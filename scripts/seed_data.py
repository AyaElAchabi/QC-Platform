"""
Seed database with initial data
Run from HOST machine (not in container)
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

# Models
from backend.models.user import User, UserRole
from backend.models.project import Product, Class
from backend.services.auth.rbac import hash_password

# Database connection (localhost since we're on host)
DATABASE_URL = "postgresql://admin:secret@localhost:5432/mlops_qc"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # Check if data already exists
        existing_admin = db.query(User).filter(User.email == "admin@mlops-qc.com").first()
        if existing_admin:
            print("⚠️  Data already exists. Skipping seed.")
            return
        
        # Create admin user
        admin = User(
            email="admin@mlops-qc.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            full_name="Admin User",
            is_active=True,
            email_verified=True
        )
        db.add(admin)
        
        # Create operator user
        operator = User(
            email="operator@mlops-qc.com",
            password_hash=hash_password("operator123"),
            role=UserRole.OPERATOR,
            full_name="Operator User",
            is_active=True,
            email_verified=True
        )
        db.add(operator)
        
        # Create viewer user
        viewer = User(
            email="viewer@mlops-qc.com",
            password_hash=hash_password("viewer123"),
            role=UserRole.VIEWER,
            full_name="Viewer User",
            is_active=True,
            email_verified=True
        )
        db.add(viewer)
        
        # Create sample products
        electronics = Product(
            name="Electronics PCB",
            type="electronics",
            description="Printed Circuit Board inspection"
        )
        db.add(electronics)
        db.flush()
        
        textile = Product(
            name="Textile Fabric",
            type="textile",
            description="Fabric defect inspection"
        )
        db.add(textile)
        db.flush()
        
        # Create sample classes for electronics
        electronics_classes = [
            Class(product_id=electronics.id, name="scratch", color_hex="#FF5733", severity="minor"),
            Class(product_id=electronics.id, name="crack", color_hex="#C70039", severity="critical"),
            Class(product_id=electronics.id, name="discoloration", color_hex="#FFC300", severity="major"),
            Class(product_id=electronics.id, name="missing_component", color_hex="#900C3F", severity="critical"),
        ]
        db.add_all(electronics_classes)
        
        # Create sample classes for textile
        textile_classes = [
            Class(product_id=textile.id, name="hole", color_hex="#581845", severity="critical"),
            Class(product_id=textile.id, name="stain", color_hex="#DAF7A6", severity="major"),
            Class(product_id=textile.id, name="thread_pull", color_hex="#33FF57", severity="minor"),
        ]
        db.add_all(textile_classes)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print("\n📧 Test credentials:")
        print("   Admin:    admin@mlops-qc.com / admin123")
        print("   Operator: operator@mlops-qc.com / operator123")
        print("   Viewer:   viewer@mlops-qc.com / viewer123")
        print("\n📦 Sample data:")
        print(f"   - 2 Products (Electronics, Textile)")
        print(f"   - 7 Defect Classes")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()