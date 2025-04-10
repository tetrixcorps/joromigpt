# scripts/data_pipeline.py
import os
import argparse
import logging
from src.backend.ai.data_processing.db_processor import DataProcessor
from src.backend.ai.utils.db_connector import DatabaseConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Data Pipeline for AI Training")
    parser.add_argument("--query", type=str, help="SQL query to fetch data")
    parser.add_argument("--query-file", type=str, help="File containing SQL query")
    parser.add_argument("--output", type=str, required=True, help="Output path for processed data")
    parser.add_argument("--weaviate-class", type=str, help="Weaviate class to fetch data from")
    parser.add_argument("--weaviate-properties", type=str, help="Comma-separated list of Weaviate properties")
    args = parser.parse_args()
    
    # Initialize processor
    processor = DataProcessor()
    
    # Process data from PostgreSQL
    if args.query or args.query_file:
        query = args.query
        if args.query_file:
            with open(args.query_file, 'r') as f:
                query = f.read()
                
        if not query:
            logger.error("No query provided")
            return 1
            
        output_path = processor.process_and_save_for_training(query, args.output)
        if not output_path:
            logger.error("Failed to process data")
            return 1
            
        logger.info(f"Data pipeline completed successfully. Output: {output_path}")
        return 0
        
    # Process data from Weaviate
    elif args.weaviate_class and args.weaviate_properties:
        db_connector = DatabaseConnector()
        client = db_connector.connect_to_weaviate()
        if not client:
            logger.error("Failed to connect to Weaviate")
            return 1
            
        properties = args.weaviate_properties.split(',')
        vector_data = db_connector.fetch_vector_data(client, args.weaviate_class, properties)
        
        if not vector_data:
            logger.error("No data retrieved from Weaviate")
            return 1
            
        # Convert to DataFrame and process
        import pandas as pd
        df = pd.DataFrame(vector_data)
        
        # Save processed data
        if args.output.endswith('.jsonl'):
            df.to_json(args.output, orient='records', lines=True)
        elif args.output.endswith('.csv'):
            df.to_csv(args.output, index=False)
        else:
            # Default to jsonl
            output_path = args.output + '.jsonl'
            df.to_json(output_path, orient='records', lines=True)
            
        logger.info(f"Data pipeline completed successfully. Output: {args.output}")
        return 0
    
    else:
        logger.error("Either PostgreSQL query or Weaviate class must be provided")
        return 1

if __name__ == "__main__":
    exit(main())