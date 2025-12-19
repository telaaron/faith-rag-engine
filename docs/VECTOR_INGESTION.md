# 🧬 From Scripture to Vectors: The Ingestion Process

This document explains the technical process of converting the raw text of the King James Version (KJV) Bible into a queryable Vector Database. This is the core engine that allows our AI to "understand" and retrieve relevant scripture based on semantic meaning rather than just keywords.

## 1. The Data Source 📜
We start with a structured JSON file of the Bible (`bible_kjv.json`).
The structure is hierarchical:
```json
[
  {
    "name": "Genesis",
    "chapters": [
      [ "In the beginning God created...", "And the earth was without form..." ],
      [ "Thus the heavens and the earth..." ]
    ]
  },
  ...
]
```

## 2. The Ingestion Pipeline ⚙️

The transformation happens in `backend/app/ingest.py`. Here is the step-by-step process:

### Step A: Granularity (Chunking)
We made a specific design decision to treat **each individual verse** as a separate document.
*   **Why?** Precision. When a user asks about "anxiety", we want to retrieve specific verses that address it, not entire chapters which might dilute the context.
*   **Result:** Approximately 31,000 individual documents (verses).

### Step B: Metadata Enrichment
For every verse, we attach metadata. This is crucial for the AI to be able to cite the source correctly later.
*   **Content**: "The Lord is my shepherd; I shall not want."
*   **Metadata**:
    *   `book`: "Psalms"
    *   `chapter`: 23
    *   `verse`: 1
    *   `citation`: "Psalms 23:1"

### Step C: Embedding (Vectorization)
We use **HuggingFace Embeddings** (specifically `sentence-transformers`) to convert the text of each verse into a high-dimensional vector (a list of numbers).
*   **Model**: These models are trained to place semantically similar text close together in vector space.
*   **Example**: The vector for "The Lord is my shepherd" will be mathematically close to a vector for "God takes care of me", even though they share few words.

### Step D: Indexing (FAISS)
We use **FAISS (Facebook AI Similarity Search)** to store these vectors efficiently.
*   FAISS allows for extremely fast "Nearest Neighbor" search.
*   When a user queries the system, we convert their question into a vector and ask FAISS: *"Which 5 verses are mathematically closest to this question?"*

## 3. Why this ensures Safety 🛡️
By strictly limiting the AI's context to *only* the verses retrieved from this verified database, we prevent the model from hallucinating theology. It acts as a **Retrieval Augmented Generation (RAG)** system:

1.  **Retrieve**: Get the 3-5 most relevant verses from our FAISS index.
2.  **Augment**: Paste these verses into the prompt.
3.  **Generate**: Ask the AI to answer the user *using only the verses provided*.

---
*See `backend/app/ingest.py` for the implementation code.*
