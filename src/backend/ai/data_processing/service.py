# src/backend/ai/data_processing/service.py
import os
import logging
import json
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
import cudf
import cuml
import numpy as np
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAPIDS Data Processing Service")

class DataProcessRequest(BaseModel):
    data: List[Dict[str, Any]]
    operations: List[str]
    output_format: str = "json"

class DatasetAnalysisRequest(BaseModel):
    dataset_path: str
    analysis_type: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "rapids-processing", 
        "cuda_available": True
    }

@app.post("/process")
async def process_data(request: DataProcessRequest):
    try:
        # Convert input data to cuDF DataFrame
        df = cudf.DataFrame(request.data)
        
        # Apply requested operations
        for operation in request.operations:
            if operation == "dropna":
                df = df.dropna()
            elif operation == "normalize":
                # Normalize numeric columns
                numeric_cols = df.select_dtypes(include=['int', 'float']).columns
                for col in numeric_cols:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    df[col] = (df[col] - min_val) / (max_val - min_val)
            elif operation.startswith("fillna:"):
                # Fill NA values with specified value
                value = operation.split(":")[1]
                try:
                    value = float(value)
                except ValueError:
                    pass  # Keep as string if not convertible to float
                df = df.fillna(value)
        
        # Convert back to desired format
        if request.output_format == "json":
            result = df.to_pandas().to_dict(orient="records")
        else:
            # Default to JSON if format not recognized
            result = df.to_pandas().to_dict(orient="records")
            
        return {"processed_data": result, "row_count": len(result)}
    
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_dataset(request: DatasetAnalysisRequest, background_tasks: BackgroundTasks):
    try:
        # Load dataset using cuDF
        if request.dataset_path.endswith('.csv'):
            df = cudf.read_csv(request.dataset_path)
        elif request.dataset_path.endswith('.parquet'):
            df = cudf.read_parquet(request.dataset_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        if request.analysis_type == "statistics":
            # Calculate basic statistics
            stats = {}
            numeric_cols = df.select_dtypes(include=['int', 'float']).columns
            
            for col in numeric_cols:
                stats[col] = {
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
            
            return {"statistics": stats}
            
        elif request.analysis_type == "kmeans":
            # Perform K-means clustering (as a background task)
            background_tasks.add_task(perform_kmeans, df, request.dataset_path)
            return {"status": "K-means clustering started in background"}
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported analysis type")
    
    except Exception as e:
        logger.error(f"Error analyzing dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prepare-for-llm")
async def prepare_for_llm(data_path: str):
    """Process and prepare data for the LLM layer."""
    try:
        # Load data
        if data_path.endswith('.csv'):
            df = cudf.read_csv(data_path)
        elif data_path.endswith('.parquet'):
            df = cudf.read_parquet(data_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Perform common preprocessing steps:
        # 1. Drop duplicates
        df = df.drop_duplicates()
        
        # 2. Handle missing values
        df = df.fillna("N/A")  # Fill string columns
        numeric_cols = df.select_dtypes(include=['int', 'float']).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].mean())
        
        # 3. Format for LLM consumption
        # Convert to list of dictionaries for easier processing by LLMs
        processed_data = df.to_pandas().to_dict(orient="records")
        
        # Save processed data
        output_path = data_path.replace(".", "_processed.")
        if output_path.endswith('_processed.csv'):
            cudf.DataFrame.from_pandas(processed_data).to_csv(output_path, index=False)
        else:
            cudf.DataFrame.from_pandas(processed_data).to_parquet(output_path, index=False)
            
        return {
            "status": "success", 
            "processed_path": output_path,
            "record_count": len(processed_data)
        }
    
    except Exception as e:
        logger.error(f"Error preparing data for LLM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def perform_kmeans(df, dataset_path):
    """Background task to perform K-means clustering."""
    try:
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=['int', 'float'])
        
        # Handle any remaining NaN values
        numeric_df = numeric_df.fillna(0)
        
        # Perform K-means clustering
        n_clusters = min(5, len(numeric_df))  # Choose appropriate number of clusters
        kmeans = cuml.KMeans(n_clusters=n_clusters)
        kmeans.fit(numeric_df)
        
        # Get cluster assignments
        clusters = kmeans.predict(numeric_df)
        
        # Save results
        results_path = os.path.join(os.path.dirname(dataset_path), "kmeans_results.json")
        with open(results_path, 'w') as f:
            json.dump({
                "cluster_centers": kmeans.cluster_centers_.tolist(),
                "n_clusters": n_clusters,
                "inertia": float(kmeans.inertia_)
            }, f)
        
        logger.info(f"K-means clustering completed, results saved to {results_path}")
    
    except Exception as e:
        logger.error(f"Error in K-means clustering: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("data_processing.service:app", host="0.0.0.0", port=port, reload=False)