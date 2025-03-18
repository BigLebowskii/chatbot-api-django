import os
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from django.conf import settings
from chatbot.models import Documents
import uuid

class VectorStoreService:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.persist_directory = os.path.join(settings.BASE_DIR, "chroma_db")
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )
    
    def add_documents(self, document):
        """Adds a document to the vector store (legacy method)"""
        try:
            document_id = str(document.id)
            self.vector_store.add_texts(
                texts=[document.content],
                metadatas=[{"title": document.title, "document_id": document_id}],
                ids=[document_id]
            )
            return True
        except Exception as e:
            print(f"Error adding document to vector store: {e}")
            return False
    
    def add_document_chunks(self, document_id, text_chunks):
        """Add document chunks to the vector store"""
        try:
            # Get document for metadata
            document = Documents.objects.get(id=document_id)
            
            # Create metadata for each chunk
            metadatas = [
                {
                    "title": document.title, 
                    "document_id": str(document_id), 
                    "chunk_id": i
                } for i in range(len(text_chunks))
            ]
            
            # Create unique IDs for each chunk
            ids = [f"{document_id}_{i}" for i in range(len(text_chunks))]
            
            # Add chunks to vector store
            self.vector_store.add_texts(
                texts=text_chunks,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error adding document chunks to vector store: {e}")
            return False
    
    def search_documents(self, query, k=3):
        """Search for similar docs"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def delete_document(self, document_id):
        """Delete a document from the vector store"""
        try:
            # First try to delete any chunks belonging to this document
            document_id_str = str(document_id)
            
            # Use filter to find all chunks with this document_id
            results = self.vector_store.get(where={"document_id": document_id_str})
            if results and 'ids' in results and results['ids']:
                # Delete all found chunks
                self.vector_store.delete(ids=results['ids'])
            else:
                # Legacy: try direct ID deletion for non-chunked documents
                self.vector_store.delete([document_id_str])
                
            return True
        except Exception as e:
            print(f"Error deleting document from vector store: {e}")
            return False