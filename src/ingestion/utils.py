import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
from ..config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate if the dataframe contains all required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of column names that must be present
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False
    return True

def process_dataframe(df: pd.DataFrame, transformations: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply transformations to the dataframe.
    
    Args:
        df: DataFrame to transform
        transformations: Dictionary of column names and their transformation functions
        
    Returns:
        pd.DataFrame: Transformed dataframe
    """
    try:
        for column, transform_func in transformations.items():
            if column in df.columns:
                df[column] = df[column].apply(transform_func)
        return df
    except Exception as e:
        logger.error(f"Error applying transformations: {str(e)}")
        raise

def save_dataframe(df: pd.DataFrame, filename: str) -> bool:
    """
    Save dataframe to the output directory.
    
    Args:
        df: DataFrame to save
        filename: Name of the output file
        
    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        output_path = Path(Config.OUTPUT_PATH) / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved data to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        return False 