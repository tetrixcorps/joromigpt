# src/backend/ai/utils/db_connector.py
import os
import logging
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import weaviate

logger = logging.getLogger(__name__)

class DatabaseConnector:
    def __init__(self):
        # PostgreSQL connection parameters
        self.pg_host = os.getenv("POSTGRES_HOST", "postgres")
        self.pg_db = os.getenv("POSTGRES_DB", "training_data")
        self.pg_user = os.getenv("POSTGRES_USER", "postgres")
        self.pg_password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.pg_port = os.getenv("POSTGRES_PORT", "5432")
        
        # Weaviate connection parameters
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        
    def connect_to_postgres(self):
        """Connect to PostgreSQL database and return connection"""
        try:
            connection = psycopg2.connect(
                host=self.pg_host,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_password,
                port=self.pg_port
            )
            logger.info("Connected to PostgreSQL successfully!")
            return connection
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return None
            
    def get_sqlalchemy_engine(self):
        """Get SQLAlchemy engine for pandas operations"""
        connection_string = f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        return create_engine(connection_string)
            
    def connect_to_weaviate(self):
        """Connect to Weaviate vector database"""
        try:
            client = weaviate.Client(url=self.weaviate_url)
            logger.info("Connected to Weaviate successfully!")
            return client
        except Exception as e:
            logger.error(f"Error connecting to Weaviate: {e}")
            return None
            
    def fetch_vector_data(self, client, class_name, properties, limit=10000):
        """Fetch data from Weaviate class"""
        try:
            result = (
                client.query
                .get(class_name, properties)
                .with_limit(limit)
                .do()
            )
            return result["data"]["Get"][class_name]
        except Exception as e:
            logger.error(f"Error fetching data from Weaviate: {e}")
            return []