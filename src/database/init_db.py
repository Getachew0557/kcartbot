from src.database.models import Base
from src.database import engine

def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()