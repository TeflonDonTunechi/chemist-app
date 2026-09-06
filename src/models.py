from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default='cashier')
    is_approved = Column(Boolean, default=False)

class Drug(Base):
    __tablename__ = 'drug'
    id = Column(Integer, primary_key=True)
    brand_name = Column(String(100), nullable=False)
    drug_name = Column(String(100), nullable=False)
    strength = Column(String(50))
    dosing_bands = Column(String(200))
    moa = Column(String(200))
    unit_price = Column(Float, nullable=False)

class StockLot(Base):
    __tablename__ = 'stock_lot'
    id = Column(Integer, primary_key=True)
    drug_id = Column(Integer, ForeignKey('drug.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=False)
    date_added = Column(DateTime, default=datetime.utcnow)
    drug = relationship('Drug', backref='lots')

class Sale(Base):
    __tablename__ = 'sale'
    id = Column(Integer, primary_key=True)
    cashier_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sale_type = Column(String(20), default='drug')
    cashier = relationship('User', backref='sales')

class SaleItem(Base):
    __tablename__ = 'sale_item'
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sale.id'), nullable=False)
    drug_id = Column(Integer, ForeignKey('drug.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    lot_id = Column(Integer, ForeignKey('stock_lot.id'))
    sale = relationship('Sale', backref='items')
    drug = relationship('Drug')

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(120), nullable=False)
    subject = Column(String(200))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    action = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)