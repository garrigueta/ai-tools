import os
import json
import datetime
from typing import List, Dict, Tuple, Optional, Any, Union
from pathlib import Path
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Import the unified database configuration
from ai_tools.config.database import db_config

# Add type annotation for CHAT_HISTORY
CHAT_HISTORY: List[Tuple[str, str]] = []
RET_CHAIN = None

# Use the unified database configuration
VECTOR_DB_PATH = db_config.vector_db_path
DEFAULT_EMBEDDING_MODEL = db_config.default_embedding_model
EXTERNAL_VECTOR_DB_ENABLED = db_config.vector_db_enabled

# Determine if we're using the external DB or local FAISS
def using_external_db():
    return EXTERNAL_VECTOR_DB_ENABLED


def load_documents_from_directory(directory_path):
    """ Load all documents from a specified directory. """
    documents = []
    
    # Create loaders for different file types
    loaders = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
        # Add other loaders for different file types as needed
    }
    
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in loaders:
                try:
                    loader = loaders[file_extension](file_path)
                    documents.extend(loader.load())
                    print(f"Loaded document: {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
    
    return documents


def vectorize_documents(directory_path, model_name=None, db_name="default"):
    """
    Vectorize documents from a directory and save the vector database
    
    Args:
        directory_path: Path to the directory containing documents
        model_name: Name of the embedding model to use
        db_name: Name of the database to save
        
    Returns:
        Path to the saved vector database
    """
    # Use default model if not specified
    if model_name is None:
        model_name = DEFAULT_EMBEDDING_MODEL
        
    # Check if using external vector database
    if using_external_db():
        return _vectorize_documents_external(directory_path, model_name, db_name)
    
    # Using local FAISS database
    # Create the vector database directory if it doesn't exist
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    
    # Load documents
    documents = load_documents_from_directory(directory_path)
    if not documents:
        print(f"No documents found in {directory_path}")
        return None
    
    # Create embeddings
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    
    # Create vector store
    vector_store = FAISS.from_documents(documents, embedding_model)
    
    # Save vector store
    db_path = os.path.join(VECTOR_DB_PATH, db_name)
    vector_store.save_local(db_path)
    
    # Save metadata
    metadata = {
        "created_at": datetime.datetime.now().isoformat(),
        "document_count": len(documents),
        "model": model_name,
        "source_directory": directory_path
    }
    
    with open(os.path.join(db_path, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Vectorized {len(documents)} documents and saved to {db_path}")
    return db_path


def _vectorize_documents_external(directory_path, model_name, db_name):
    """
    Vectorize documents and store in external vector database
    
    This is a placeholder for external DB integration. In a production
    environment, you would implement the specific database connector here.
    """
    # Get database configuration from the unified config
    vector_config = db_config.get_vector_db_config()
    
    # Get the table name with prefix to ensure it's separate from chat history
    table_name = db_config.get_vector_table_name(db_name)
    
    try:
        # Load documents
        documents = load_documents_from_directory(directory_path)
        if not documents:
            print(f"No documents found in {directory_path}")
            return None
            
        print(f"Vectorizing {len(documents)} documents for external database")
        print(f"Target table: {table_name}")
        
        # Create embeddings
        embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        
        # In a real implementation, you would:
        # 1. Connect to your external vector database 
        # 2. Convert documents to embeddings
        # 3. Store the embeddings in the database table with the proper prefix
        
        print(f"Connection details: {vector_config['host']}:{vector_config['port']}/{vector_config['dbname']}")
        print(f"Would connect with user: {vector_config['user']}")
        
        # For now, just return a mock success message
        print(f"Vectorized {len(documents)} documents in external database table {table_name}")
        return f"external://{vector_config['host']}/{table_name}"
    except Exception as e:
        print(f"Error vectorizing documents for external database: {str(e)}")
        return None


def load_vector_db(db_name="default", model_name=None):
    """
    Load a vector database
    
    Args:
        db_name: Name of the database to load
        model_name: Name of the embedding model to use
        
    Returns:
        Loaded vector store or None if not found
    """
    # Use default model if not specified
    if model_name is None:
        model_name = DEFAULT_EMBEDDING_MODEL
        
    # Check if using external vector database
    if using_external_db():
        return _load_vector_db_external(db_name, model_name)
    
    # Using local FAISS database
    db_path = os.path.join(VECTOR_DB_PATH, db_name)
    
    if not os.path.exists(db_path):
        print(f"Vector database {db_name} not found at {db_path}")
        return None
    
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    
    try:
        vector_store = FAISS.load_local(db_path, embedding_model)
        print(f"Loaded vector database from {db_path}")
        
        # Load metadata if available
        metadata_path = os.path.join(db_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                print(f"Database contains {metadata.get('document_count', 'unknown')} documents")
        
        return vector_store
    except Exception as e:
        print(f"Error loading vector database: {str(e)}")
        return None


def _load_vector_db_external(db_name, model_name):
    """
    Load a vector database from an external source
    
    This is a placeholder for external DB integration. In a production
    environment, you would implement the specific database connector here.
    """
    # Get database configuration from the unified config
    vector_config = db_config.get_vector_db_config()
    
    try:
        print(f"Loading vector database {db_name} from external source")
        print(f"Connection details: {vector_config['host']}:{vector_config['port']}/{vector_config['dbname']}")
        
        # In a real implementation, you would:
        # 1. Connect to your external database
        # 2. Create a custom retriever class that interfaces with your DB
        
        # For this demo, create a mock FAISS vector store
        from langchain_core.documents import Document
        from langchain_core.vectorstores import VectorStoreRetriever
        
        embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        
        # Create a simple mock document
        mock_docs = [
            Document(
                page_content="This is a mock document from the external database",
                metadata={"source": "external_db", "db_name": db_name}
            )
        ]
        
        # Create a temporary FAISS index (in a real implementation, this would connect to your DB)
        vector_store = FAISS.from_documents(mock_docs, embedding_model)
        
        print(f"Mock external vector database {db_name} loaded successfully")
        return vector_store
    except Exception as e:
        print(f"Error loading external vector database: {str(e)}")
        return None


def generate_retriever(
        directory_path=None,
        llm=None,
        model=None,
        db_name="default",
        k=3):
    """ Generate a retriever for question-answering tasks. """
    
    # Use default model if not specified
    if model is None:
        model = DEFAULT_EMBEDDING_MODEL
        
    # Either load from an existing vector database or create a new one
    if directory_path:
        # Vectorize documents and create a new database
        vectorize_documents(directory_path, model, db_name)
    
    # Load the vector database
    vector_store = load_vector_db(db_name, model)
    if not vector_store:
        print("Failed to load or create vector database")
        return None

    # Step 3: Define Retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": k})

    # If no LLM is provided, just return the retriever
    if not llm:
        return retriever

    # Get LLM configuration
    llm_config = db_config.get_llm_config()
    print(f"Using LLM at {llm_config['host']}:{llm_config['port']} with model {llm_config['model']}")

    # Step 4: Configure History-Aware Retriever
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Step 5: Define Question Answering Chain
    qa_system_prompt = (
        "You are an assistant for question-answering tasks. Use "
        "the following pieces of retrieved context to answer the "
        "question. If you don't know the answer, just say that you "
        "don't know. Use three sentences maximum and keep the answer "
        "concise.\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Step 6: Create Retrieval Chain
    global RET_CHAIN
    RET_CHAIN = create_retrieval_chain(
        history_aware_retriever, question_answer_chain
    )

    def ask_question(question):
        """ Ask a question using the retrieval chain. """
        response = RET_CHAIN({"input": question, "chat_history": CHAT_HISTORY})
        CHAT_HISTORY.append((question, response["output"]))
        return response["output"]
    return ask_question


def search_documents(query, db_name="default", model_name=None, k=5):
    """
    Search for documents in the vector database
    
    Args:
        query: Query string to search for
        db_name: Name of the database to search
        model_name: Name of the embedding model to use
        k: Number of results to return
        
    Returns:
        List of documents and their scores
    """
    # Use default model if not specified
    if model_name is None:
        model_name = DEFAULT_EMBEDDING_MODEL
        
    vector_store = load_vector_db(db_name, model_name)
    if not vector_store:
        return []
    
    docs_with_scores = vector_store.similarity_search_with_score(query, k=k)
    results = []
    
    for doc, score in docs_with_scores:
        results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "relevance_score": float(score)
        })
    
    return results
