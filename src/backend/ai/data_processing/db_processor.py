# src/backend/ai/data_processing/db_processor.py
import os
import logging
import pandas as pd
import cudf
from typing import List, Dict, Any, Optional
from ..utils.db_connector import DatabaseConnector
from ..utils.rapids_client import RapidsClient

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.db_connector = DatabaseConnector()
        self.rapids_client = RapidsClient()
        
    def fetch_and_process_data(self, query, use_rapids=True):
        """Fetch data from PostgreSQL and process with RAPIDS"""
        # Connect to database
        connection = self.db_connector.connect_to_postgres()
        if not connection:
            logger.error("Failed to connect to database")
            return None
            
        try:
            # Fetch data as pandas DataFrame
            logger.info(f"Executing query: {query}")
            df = pd.read_sql(query, connection)
            logger.info(f"Retrieved {len(df)} rows from database")
            
            if use_rapids:
                # Process with RAPIDS (GPU)
                try:
                    # Convert to cuDF for GPU acceleration
                    gdf = cudf.DataFrame.from_pandas(df)
                    
                    # Perform GPU-accelerated operations
                    gdf = gdf.drop_duplicates()
                    
                    # Handle missing values
                    gdf = gdf.fillna("N/A")  # Fill string columns
                    numeric_cols = gdf.select_dtypes(include=['int', 'float']).columns
                    for col in numeric_cols:
                        gdf[col] = gdf[col].fillna(gdf[col].mean())
                    
                    # Convert back to pandas for compatibility
                    processed_df = gdf.to_pandas()
                    logger.info("Data processed successfully with GPU acceleration")
                    return processed_df
                    
                except Exception as e:
                    logger.warning(f"GPU processing failed, falling back to CPU: {e}")
                    # Fall back to CPU processing
            
            # CPU processing (fallback)
            df = df.drop_duplicates()
            df = df.fillna("N/A")
            numeric_cols = df.select_dtypes(include=['int', 'float']).columns
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].mean())
                
            logger.info("Data processed successfully with CPU")
            return df
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return None
        finally:
            connection.close()
            
    def process_and_save_for_training(self, query, output_path):
        """Process data and save for model training"""
        processed_df = self.fetch_and_process_data(query)
        if processed_df is not None:
            # Save to file for training
            if output_path.endswith('.jsonl'):
                processed_df.to_json(output_path, orient='records', lines=True)
            elif output_path.endswith('.csv'):
                processed_df.to_csv(output_path, index=False)
            elif output_path.endswith('.parquet'):
                processed_df.to_parquet(output_path, index=False)
            else:
                # Default to jsonl
                output_path = output_path + '.jsonl'
                processed_df.to_json(output_path, orient='records', lines=True)
                
            logger.info(f"Processed data saved to {output_path}")
            return output_path
        return None