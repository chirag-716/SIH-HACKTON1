#!/usr/bin/env python3
"""
GUVNL Queue Management System - Main Application Entry Point
"""

import os
from dotenv import load_dotenv
from app import create_app, db, socketio, make_celery

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Initialize Celery with Flask app context
celery = make_celery(app)

@app.before_first_request
def create_tables():
    """Create database tables on first request"""
    db.create_all()

@app.cli.command()
def init_db():
    """Initialize the database with tables and seed data"""
    print("Creating database tables...")
    db.create_all()
    
    # Import and run seed data
    try:
        from app.services.database_service import initialize_default_data
        initialize_default_data()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.cli.command()
def reset_db():
    """Reset the database (drop all tables and recreate)"""
    print("WARNING: This will delete all data in the database!")
    confirm = input("Are you sure? (y/N): ")
    if confirm.lower() == 'y':
        print("Dropping all tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        
        try:
            from app.services.database_service import initialize_default_data
            initialize_default_data()
            print("Database reset successfully!")
        except Exception as e:
            print(f"Error resetting database: {e}")
    else:
        print("Database reset cancelled.")

if __name__ == '__main__':
    # Run the application
    if os.getenv('FLASK_ENV') == 'development':
        # Development server with hot reload
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=True,
            use_reloader=True
        )
    else:
        # Production server
        socketio.run(
            app,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=False
        )