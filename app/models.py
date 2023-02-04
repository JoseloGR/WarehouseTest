from .database import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, ForeignKey, text
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, nullable=False)
    sku = Column(String, nullable=False, unique=True)
    inventories = relationship('Inventory', backref='product')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_onupdate=text("now()"))

class Warehouse(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True, nullable=False)
    sub_inventory = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    inventories = relationship('Inventory', backref='warehouse')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_onupdate=text("now()"))

class Inventory(Base):
    __tablename__ = 'inventories'
    id = Column(Integer, primary_key=True, nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_onupdate=text("now()"))
