import sqlalchemy
from sqlalchemy.orm import declarative_base, Session

# --- IMPORTANT: Make sure this line is 100% correct ---
DATABASE_URL = "postgresql://reyhane:password123@localhost/location_app_db"

try:
    # Try to create an engine and connect
    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("✅  Connection successful!")

        # Define the tables
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'user'
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(80), unique=True, nullable=False)
            password_hash = sqlalchemy.Column(sqlalchemy.String(120), nullable=False)

        class SavedPlace(Base):
            __tablename__ = 'saved_place'
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            place_name = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
            tags = sqlalchemy.Column(sqlalchemy.String(200))
            user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'), nullable=False)

        # Create the tables
        Base.metadata.create_all(engine)
        print("✅  Tables created successfully (or already exist).")

except Exception as e:
    print("❌  An error occurred:")
    print(e)