import json
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Configuration
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/bible_kjv.json")
DB_PATH = "faiss_index"

def load_bible_data(filepath):
    """Reads the JSON bible structure."""
    print(f"📖 Loading Bible text from {filepath}...")
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data

def process_documents(bible_data):
    """Converts JSON to LangChain Documents."""
    documents = []
    print("⚙️ Processing verses...")
    
    # Structure: List of books -> "chapters" -> List of chapters -> List of verses
    for book in bible_data:
        book_name = book.get("name", "Unknown")
        chapters = book.get("chapters", [])
        
        for chapter_idx, verses in enumerate(chapters):
            chapter_num = chapter_idx + 1
            
            for verse_idx, text in enumerate(verses):
                verse_num = verse_idx + 1
                
                # Create one document per verse
                # Metadata is important for citation!
                doc = Document(
                    page_content=text,
                    metadata={
                        "book": book_name,
                        "chapter": chapter_num,
                        "verse": verse_num,
                        "citation": f"{book_name} {chapter_num}:{verse_num}"
                    }
                )
                documents.append(doc)
                
    print(f"✅ {len(documents)} verses processed.")
    return documents

def main():
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: File {DATA_PATH} not found.")
        return

    data = load_bible_data(DATA_PATH)
    
    # 2. Process Documents
    documents = process_documents(data)
    
    # 3. Create Embeddings
    print("🧠 Generating Embeddings (this may take a while)...")
    # Using a multilingual model is fine, but we could switch to an English one if desired.
    # Keeping it for simplicity as it works well.
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    # 4. Create Vector Store
    vector_store = FAISS.from_documents(documents, embeddings)
    
    # 5. Save
    vector_store.save_local(DB_PATH)
    print(f"💾 Database saved to '{DB_PATH}'.")

if __name__ == "__main__":
    main()
