from database.connection import db_manager

def main():
    print("Initializing database...")
    db_manager.init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    main() 