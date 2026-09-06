# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from src.models import Base, Drug, StockLot, User

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'pharma_pos.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

def init_db():
    # Create all tables
    Base.metadata.create_all(engine)
    sess = Session()
    
    # Create admin with new password
    if not sess.query(User).filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('zeitgeist'),
            role='admin',
            is_approved=True
        )
        sess.add(admin)
    
    # Create cashier (optional)
    if not sess.query(User).filter_by(username='cashier1').first():
        cashier = User(
            username='cashier1',
            password_hash=generate_password_hash('cashier123'),
            role='cashier',
            is_approved=True
        )
        sess.add(cashier)
    
    # NO DEFAULT DRUGS - inventory starts blank
    # Users must add drugs manually or via CSV import
    
    sess.commit()
    sess.close()