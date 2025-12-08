"""LLM engine service for OpenAI integration."""
from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings

class LLMEngine:
    """Service for LLM operations using OpenAI."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        
        # Initialize OpenAI client with optional base URL
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
        
        self.client = OpenAI(**client_kwargs)
        self.model = settings.LLM_MODEL
    
    def generate_answer(
        self,
        query: str,
        context: List[Dict[str, Any]],
        language: str = "hu"
    ) -> str:
        """
        Generate an answer using the LLM with retrieved context.
        
        Args:
            query: User's query
            context: List of retrieved documents with metadata
            language: Language code (hu or en)
            
        Returns:
            Generated answer string
        """
        # Build context string from retrieved documents
        context_parts = []
        for i, doc in enumerate(context, 1):
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")
            
            context_part = f"[{i}] "
            if metadata.get("DisplayName"):
                context_part += f"Név: {metadata['DisplayName']}\n"
            if metadata.get("Title"):
                context_part += f"Beosztás: {metadata['Title']}\n"
            if metadata.get("Department"):
                context_part += f"Tanszék: {metadata['Department']}\n"
            if metadata.get("Company"):
                context_part += f"Kar: {metadata['Company']}\n"
            if metadata.get("TelephoneNumber"):
                context_part += f"Telefonszám: {metadata['TelephoneNumber']}\n"
            if metadata.get("UPN"):
                context_part += f"Email: {metadata['UPN']}\n"
            
            context_parts.append(context_part)
        
        context_text = "\n\n".join(context_parts)
        
        # Build system prompt based on language
        if language == "hu":
            system_prompt = """Te az Óbudai Egyetem segítőkész telefonkönyv asszisztense vagy. 
A feladatod, hogy segíts a felhasználóknak megtalálni a keresett személyek elérhetőségeit.

FONTOS SZABÁLYOK:
1. Szigorúan csak a megadott kontextusból válaszolj. Ne találj ki információkat!
2. Ha a keresett információ nincs a kontextusban, mondd el, hogy nem található.
3. A válaszodban mindig tüntesd fel a pontos telefonszámot és email címet, ha elérhető.
4. Legyél barátságos és segítőkész.
5. Ha több találat van, sorold fel őket egyértelműen."""
            
            user_prompt = f"""A felhasználó kérdése: {query}

Elérhető információk a telefonkönyvből:
{context_text}

Kérlek, válaszolj a felhasználó kérdésére a fenti információk alapján."""
        else:  # English
            system_prompt = """You are a helpful phonebook assistant for Óbuda University.
Your task is to help users find contact information for the people they are looking for.

IMPORTANT RULES:
1. Answer strictly only from the provided context. Do not make up information!
2. If the requested information is not in the context, tell the user it was not found.
3. Always include the exact phone number and email address in your response if available.
4. Be friendly and helpful.
5. If there are multiple matches, list them clearly."""
            
            user_prompt = f"""User's question: {query}

Available information from the phonebook:
{context_text}

Please answer the user's question based on the above information."""
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()

