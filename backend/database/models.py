from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

# Create Base here to avoid circular imports
Base = declarative_base()

class Client(Base):
    __tablename__ = "client"
    
    client_id = Column(String(255), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    business_interests = relationship("BusinessInterest", back_populates="client", cascade="all, delete-orphan")
    analysis_sessions = relationship("AnalysisSession", back_populates="client", cascade="all, delete-orphan")
    client_sources = relationship("ClientSource", back_populates="client", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "source"
    
    source_id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String(500), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client_sources = relationship("ClientSource", back_populates="source", cascade="all, delete-orphan")

class ClientSource(Base):
    __tablename__ = "client_source"
    
    client_id = Column(String(255), ForeignKey("client.client_id"), primary_key=True)
    source_id = Column(Integer, ForeignKey("source.source_id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="client_sources")
    source = relationship("Source", back_populates="client_sources")

class BusinessInterest(Base):
    __tablename__ = "business_interest"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), ForeignKey("client.client_id"), nullable=False)
    interest_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="business_interests")
    analysis_sessions = relationship("AnalysisSession", back_populates="business_interest", cascade="all, delete-orphan")

class AnalysisSession(Base):
    __tablename__ = "analysis_session"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), ForeignKey("client.client_id"), nullable=False)
    business_interest_id = Column(Integer, ForeignKey("business_interest.id"), nullable=False)
    sources = Column(Text)  # JSON array of source URLs
    results = Column(Text)  # JSON results
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="analysis_sessions")
    business_interest = relationship("BusinessInterest", back_populates="analysis_sessions") 