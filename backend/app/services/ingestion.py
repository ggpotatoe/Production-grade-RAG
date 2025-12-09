"""Data ingestion service for processing CSV/Excel files and generating embeddings."""
import pandas as pd
from typing import List, Dict, Any, Tuple
from pathlib import Path
from fastembed import TextEmbedding
from app.config import settings
import hashlib

# Singleton embedding model cache
_embedding_model = None

def get_embedding_model():
    """Get or create singleton embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Initializing embedding model: {settings.EMBEDDING_MODEL}")
        _embedding_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
    return _embedding_model

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
    Generate embeddings for documents using FastEmbed (with cached model).
    
    Args:
        documents: List of document texts (already prefixed with "passage:")
        
    Returns:
        List of embedding vectors
    """
    model = get_embedding_model()
    embeddings = list(model.embed(documents))
    return embeddings

def get_document_id(metadata: Dict[str, Any]) -> str:
    """
    Generate deterministic document ID based on unique fields.
    This allows deduplication and updates instead of always creating new documents.
    
    Args:
        metadata: Document metadata dictionary
        
    Returns:
        Deterministic hash-based ID
    """
    # Use UPN (email) as primary unique identifier, fallback to DisplayName
    unique_key = metadata.get('UPN', '') or metadata.get('DisplayName', '')
    if not unique_key:
        # Fallback: use all available fields
        unique_key = str(sorted(metadata.items()))
    
    # Generate deterministic hash
    return hashlib.md5(unique_key.encode('utf-8')).hexdigest()

