import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from ..config.config import Config
from .utils import validate_dataframe, process_dataframe, save_dataframe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Day1Ingestion:
    def __init__(self):
        self.config = Config
        self.config.ensure_directories()
        self.required_columns = [
            'timestamp',
            'value',
            'source',
            'metadata'
        ]
        
    def load_data(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from a single file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            pd.DataFrame: Loaded dataframe
        """
        try:
            df = pd.read_csv(file_path)
            if not validate_dataframe(df, self.required_columns):
                raise ValueError(f"Invalid data format in {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise
            
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply transformations to the data.
        
        Args:
            df: DataFrame to transform
            
        Returns:
            pd.DataFrame: Transformed dataframe
        """
        transformations = {
            'timestamp': pd.to_datetime,
            'value': float,
            'metadata': lambda x: eval(x) if isinstance(x, str) else x
        }
        return process_dataframe(df, transformations)
        
    def process_file(self, file_path: Path) -> bool:
        """
        Process a single file through the ingestion pipeline.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            bool: True if processing successful, False otherwise
        """
        try:
            # Load data
            df = self.load_data(file_path)
            
            # Transform data
            df = self.transform_data(df)
            
            # Save processed data
            output_filename = f"processed_{file_path.name}"
            return save_dataframe(df, output_filename)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return False
            
    def run(self):
        """
        Run the Day 1 ingestion pipeline.
        """
        try:
            # Get list of files to process
            data_path = Path(self.config.DATA_SOURCE_PATH)
            files_to_process = list(data_path.glob(self.config.DATA_FILE_PATTERN))
            
            if not files_to_process:
                logger.warning(f"No files found matching pattern {self.config.DATA_FILE_PATTERN}")
                return
                
            logger.info(f"Found {len(files_to_process)} files to process")
            
            # Process files in parallel
            with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
                results = list(tqdm(
                    executor.map(self.process_file, files_to_process),
                    total=len(files_to_process),
                    desc="Processing files"
                ))
                
            # Log results
            successful = sum(results)
            logger.info(f"Successfully processed {successful} out of {len(files_to_process)} files")
            
        except Exception as e:
            logger.error(f"Error in ingestion pipeline: {str(e)}")
            raise

if __name__ == "__main__":
    ingestion = Day1Ingestion()
    ingestion.run() 