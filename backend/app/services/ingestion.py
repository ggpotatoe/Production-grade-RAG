"""Data ingestion service for processing CSV/Excel files and generating embeddings."""
import pandas as pd
from typing import List, Dict, Any, Tuple
from pathlib import Path
from fastembed import TextEmbedding
from app.config import settings

def process_data_file(file_path: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Process the data file (Excel/CSV) and create semantic documents.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        Tuple of (documents, metadatas) where:
        - documents: List of semantic text representations
        - metadatas: List of metadata dictionaries
    """
    file_path_obj = Path(file_path)
    
    # Read the file based on extension
    if file_path_obj.suffix.lower() == '.xlsx':
        df = pd.read_excel(file_path)
    elif file_path_obj.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path_obj.suffix}")
    
    documents = []
    metadatas = []
    
    for _, row in df.iterrows():
        # Create semantic document text
        parts = []
        
        if pd.notna(row.get('DisplayName')):
            parts.append(f"Név: {row['DisplayName']}")
        if pd.notna(row.get('Title')):
            parts.append(f"Beosztás: {row['Title']}")
        if pd.notna(row.get('Department')):
            parts.append(f"Tanszék: {row['Department']}")
        if pd.notna(row.get('Company')):
            parts.append(f"Kar: {row['Company']}")
        if pd.notna(row.get('TelephoneNumber')):
            parts.append(f"Telefonszám: {row['TelephoneNumber']}")
        if pd.notna(row.get('UPN')):
            parts.append(f"Email: {row['UPN']}")
        if pd.notna(row.get('OUPath')):
            parts.append(f"Szervezeti egység: {row['OUPath']}")
        
        # Create semantic document with "passage:" prefix for E5 model
        content = ", ".join(parts)
        document = f"passage: {content}"
        documents.append(document)
        
        # Store metadata (clean NaN values)
        metadata = {
            'DisplayName': str(row.get('DisplayName', '')) if pd.notna(row.get('DisplayName')) else '',
            'Title': str(row.get('Title', '')) if pd.notna(row.get('Title')) else '',
            'Department': str(row.get('Department', '')) if pd.notna(row.get('Department')) else '',
            'Company': str(row.get('Company', '')) if pd.notna(row.get('Company')) else '',
            'TelephoneNumber': str(row.get('TelephoneNumber', '')) if pd.notna(row.get('TelephoneNumber')) else '',
            'UPN': str(row.get('UPN', '')) if pd.notna(row.get('UPN')) else '',
            'OUPath': str(row.get('OUPath', '')) if pd.notna(row.get('OUPath')) else '',
        }
        metadatas.append(metadata)
    
    return documents, metadatas

def generate_embeddings(documents: List[str]) -> List[List[float]]:
    """
    Generate embeddings for documents using FastEmbed.
    
    Args:
        documents: List of document texts (already prefixed with "passage:")
        
    Returns:
        List of embedding vectors
    """
    embedding_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
    embeddings = list(embedding_model.embed(documents))
    return embeddings

