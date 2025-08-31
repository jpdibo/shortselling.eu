from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    flag = Column(String(10), nullable=False)
    priority = Column(String(10), default="high")  # high or low
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    short_positions = relationship("ShortPosition", back_populates="country")
    companies = relationship("Company", back_populates="country")


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    isin = Column(String(12), index=True)  # ISIN code
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    country = relationship("Country", back_populates="companies")
    short_positions = relationship("ShortPosition", back_populates="company")
    
    # Indexes
    __table_args__ = (
        Index('idx_company_country', 'country_id'),
        Index('idx_company_isin', 'isin'),
    )


class Manager(Base):
    __tablename__ = "managers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, index=True)  # For URL routing (e.g., "blackrock")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    short_positions = relationship("ShortPosition", back_populates="manager")


class ShortPosition(Base):
    __tablename__ = "short_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    position_size = Column(Float, nullable=False)  # Percentage
    is_active = Column(Boolean, default=True)  # True if from current tab/file, False if from historical tab/file
    source_url = Column(String(500))
    raw_data = Column(Text)  # Store original scraped data
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="short_positions")
    manager = relationship("Manager", back_populates="short_positions")
    country = relationship("Country", back_populates="short_positions")
    
    # Indexes
    __table_args__ = (
        Index('idx_position_date', 'date'),
        Index('idx_position_company', 'company_id'),
        Index('idx_position_manager', 'manager_id'),
        Index('idx_position_country', 'country_id'),
        Index('idx_position_active', 'is_active'),
        Index('idx_position_date_active', 'date', 'is_active'),
    )


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False, index=True)
    frequency = Column(String(20), default="daily")  # daily, weekly, monthly
    countries = Column(Text)  # JSON string of selected countries
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_subscription_email', 'email'),
        Index('idx_subscription_active', 'is_active'),
    )


class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    status = Column(String(20), nullable=False)  # success, error, partial
    records_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    country = relationship("Country")


class AnalyticsCache(Base):
    __tablename__ = "analytics_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(200), unique=True, index=True, nullable=False)
    cache_data = Column(Text, nullable=False)  # JSON string
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_cache_expires', 'expires_at'),
    )
