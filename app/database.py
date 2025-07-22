from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, UTC
import os
import psycopg2
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
logger.info(f"Looking for .env file at: {dotenv_path}")
load_dotenv(dotenv_path)

# Log environment variables (without sensitive data)
logger.info(f"DB_HOST from env: {os.getenv('DB_HOST')}")
logger.info(f"DB_DATABASE from env: {os.getenv('DB_DATABASE')}")
logger.info(f"DB_USER from env: {os.getenv('DB_USER')}")
logger.info(f"DB_PORT from env: {os.getenv('DB_PORT')}")

# Main SQLite Database URL (for app functionality)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def execute_pg_query(query: str, params: tuple = None) -> list:
    """Execute a PostgreSQL query using a new connection"""
    conn = get_bets_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            try:
                result = cur.fetchall()
                return result
            except psycopg2.ProgrammingError:
                return None  # For queries that don't return results
    finally:
        conn.close()

def get_bets_db_connection():
    """Get a connection to the PostgreSQL database for bets queries"""
    try:
        host = os.getenv('DB_HOST')
        database = os.getenv('DB_DATABASE')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        port = os.getenv('DB_PORT')

        if not all([host, database, user, password, port]):
            logger.error("Missing required database environment variables!")
            logger.error(f"Available variables: HOST={bool(host)}, DB={bool(database)}, USER={bool(user)}, PORT={bool(port)}, PASS={bool(password)}")
            raise ValueError("Missing required database environment variables")

        logger.info(f"Attempting to connect to PostgreSQL at {host}:{port}")
        
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            connect_timeout=30
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        raise

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    last_login = Column(DateTime, nullable=True)

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    description = Column(Text)
    requirements = Column(Text)  # Comma-separated list of required packages
    output_types = Column(Text)  # Expected output types: files, text, both
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

class ScriptExecution(Base):
    __tablename__ = "script_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True)  # Allow NULL for bet queries
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    arguments = Column(Text)
    output_text = Column(Text)  # stdout/stderr
    output_files = Column(Text)  # JSON list of output file paths
    return_code = Column(Integer)
    error_message = Column(Text)
    execution_time = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relationships
    script = relationship("Script")
    user = relationship("User")

class BetQuery(Base):
    __tablename__ = "bet_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, nullable=False)  # The ID being queried
    status = Column(String, nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    completed_at = Column(DateTime, nullable=True)
    email_sent = Column(Boolean, default=False)
    execution_id = Column(Integer, nullable=True)  # Add this column for file downloads
    
    # Relationship
    user = relationship("User")

class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 