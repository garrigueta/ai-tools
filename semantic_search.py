# Setup:
# python3 -m venv myenv
# source myenv/bin/activate
# pip3 install --upgrade --quiet pythondns langchain langchain-community langchain-mongodb langchain-openai pymongo faiss numpy

# Usage:
# python3 semantic_search.py

import sqlite3
import requests
import numpy as np
import faiss  # For vector search

# SQLite setup
db_path = "embeddings.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table for storing text and embeddings
cursor.execute("DROP TABLE IF EXISTS text_embeddings")
cursor.execute("""
    CREATE TABLE text_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        embedding BLOB NOT NULL
    )
""")
conn.commit()


# Custom embedding class for Ollama
class OllamaEmbeddings:
    def __init__(self, model="gemma3", host="http://localhost:11434"):
        self.model = model
        self.host = host

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            response = requests.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model, "text": text},
                timeout=10,
            )
            if response.status_code == 200:
                embeddings.append(response.json()["embedding"])
            else:
                raise requests.exceptions.RequestException(f"Failed to get embedding: {response.text}")
        return embeddings


# Texts to embed
texts = [
    "A martial artist agrees to spy on a reclusive crime lord using his invitation to a tournament there as cover.",
    "A group of intergalactic criminals are forced to work together to stop a fanatical warrior from taking control of the universe.",
    "When a boy wishes to be big at a magic wish machine, he wakes up the next morning and finds himself in an adult body.",
]

# Use Ollama for embeddings
embedding_model = OllamaEmbeddings(model="gemma3")
embeddings = embedding_model.embed_documents(texts)

# Insert documents into SQLite
for i, text in enumerate(texts):
    embedding_blob = np.array(embeddings[i], dtype=np.float32).tobytes()
    cursor.execute(
        "INSERT INTO text_embeddings (text, embedding) VALUES (?, ?)",
        (text, embedding_blob)
    )
conn.commit()

print("Documents embedded and inserted successfully.")

# Load embeddings into FAISS index
dimension = len(embeddings[0])  # Assuming all embeddings have the same dimension
index = faiss.IndexFlatL2(dimension)

# Retrieve embeddings from SQLite and add to FAISS index
cursor.execute("SELECT id, embedding FROM text_embeddings")
rows = cursor.fetchall()
ids = []
for row in rows:
    ids.append(row[0])
    embedding = np.frombuffer(row[1], dtype=np.float32)
    index.add(embedding.reshape(1, -1))  # Reshape to 2D array

# Semantic queries
semantic_queries = [
    "Secret agent captures underworld boss.",
    "Awkward team of space defenders.",
    "A magical tale of growing up.",
]

# Perform semantic search
for q in semantic_queries:
    query_embedding = embedding_model.embed_documents([q])[0]
    query_vector = np.array([query_embedding], dtype=np.float32)
    distances, indices = index.search(query_vector, k=3)  # Retrieve top 3 results

    print(f"SEMANTIC QUERY: {q}")
    print("RANKED RESULTS:")
    for i, idx in enumerate(indices[0]):
        if idx != -1:  # Check if a valid result is found
            cursor.execute("SELECT text FROM text_embeddings WHERE id = ?", (ids[idx],))
            result_text = cursor.fetchone()[0]
            print(f"{i + 1}. {result_text} (Distance: {distances[0][i]:.4f})")
    print("")

# Close SQLite connection
conn.close()
