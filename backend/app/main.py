import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

# Load environment variables from .env
# We explicitly point to the .env file in the backend directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Fix for Google Cloud Credentials path
# The library expects the path to be relative to CWD or absolute.
# We make it absolute to be safe.
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not os.path.isabs(cred_path):
        # Assuming the json file is in the same directory as .env (the 'backend' folder)
        base_dir = os.path.dirname(env_path)
        possible_path = os.path.join(base_dir, os.path.basename(cred_path))
        if os.path.exists(possible_path):
             os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = possible_path
             print(f"✅ Credentials found at: {possible_path}")
        else:
             print(f"⚠️ Warning: Credentials file not found at {possible_path}")

app = FastAPI(title="Spiritual Companion API")

# --- ADD CORS (IMPORTANT!) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (okay for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------------

# --- 1. Load Database ---
DB_PATH = "faiss_index"
print("⏳ Loading Vector Database...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # Search top 3 verses
print("✅ Database loaded.")

# --- 2. The AI Model ---
# Gemini 2.5 Flash in Frankfurt (europe-west3)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID_HERE")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west3")

llm = ChatVertexAI(
    model="gemini-2.5-flash",
    project=PROJECT_ID,
    location=LOCATION,
    temperature=0.7,
)

# --- 3. Prompt Templates (The "Soul" of the App) ---

# Template for "Mindset / Companion"
mindset_template = """You are a wise, Christian mentor.
Conversation history so far:
{history}

Current user question: {question}

Here are suitable Bible verses that you should use as a basis (only use them if they fit the current question):
{context}

Your task:
1. Answer the current question, but refer to the history.
2. Briefly explain the connection with the verses (if relevant).
3. Formulate a short, powerful prayer for the user to pray.

Formatting Rules:
- Use **bold** for key encouraging words.
- Put the prayer at the very end.
- Wrap the ENTIRE prayer in a blockquote (start lines with >).
- **IMPORTANT**: Write the prayer in the **first person** ("I", "my") so the user can read it as their own prayer to God. Do NOT pray *for* them ("I pray for my friend...").

Answer personally ("You") and encouragingly. Stick theologically to the Bible verses.
"""
mindset_prompt = ChatPromptTemplate.from_template(mindset_template)

# Template for "Theological Deep-Dive" (Explain this to me)
explain_template = """You are a theologian and Bible teacher.
Explain the verse "{question}" in mode: "{mode}".

Rules:
1. Answer DIRECTLY with the explanation. No introduction ("Sure...", "Here is...").
2. Do NOT repeat the mode name in the text.
3. Stick strictly to the chosen mode. Do NOT output anything else.

Mode Details:
- "explain_like_5": Explain it so simply that a 5-year-old child understands it. Use loving metaphors. Use **bold** for the main analogy.
- "historical": Mention only historical facts, authors, historical context, and cultural background. Factual. Use bullet points for facts if possible.
- "application": Give exactly 3 short, practical impulses for everyday life today. Format as a Markdown list (- Item).

Be brief and concise.
"""
explain_prompt = ChatPromptTemplate.from_template(explain_template)

# Template for "Prayer Architect"
prayer_template = """You are an empathetic prayer mentor.
The user wants to pray but lacks the words. Their topic: {topic}

Compose a prayer (approx. 4-6 sentences) for the user to speak:
1. Start with a personal address to God.
2. Bring the concern honestly before God.
3. Connect it with a biblical truth (comfort/hope).
4. Close with trust.

Formatting:
- Wrap the ENTIRE prayer in a blockquote (start lines with >).
- Use **bold** for 1-2 strong words of faith.
- **IMPORTANT**: Write in the **first person** ("I", "my"). The user will read this prayer. Do NOT write "I pray for this user". Write "Lord, I feel...".

Language: Natural, modern, informal (using 'You' for God).
"""
prayer_prompt = ChatPromptTemplate.from_template(prayer_template)

# --- 4. API Endpoints ---

class UserRequest(BaseModel):
    text: str
    history: str = "" # New: The chat history so far as text

class ExplainRequest(BaseModel):
    text: str
    mode: str = "application" # default

@app.get("/")
def read_root():
    return {"status": "online", "message": "Spiritual Companion API is running"}

@app.post("/api/mindset")
def get_mindset(request: UserRequest):
    """The 'Companion' mode: Gives encouragement & prayer based on Bible verses."""
    try:
        # Build RAG Chain
        chain = (
            {
                "context": itemgetter("text") | retriever, 
                "question": itemgetter("text"),
                "history": itemgetter("history")
            }
            | mindset_prompt
            | llm
            | StrOutputParser()
        )
        response = chain.invoke({"text": request.text, "history": request.history})
        
        # We also fetch the verses separately to display them in the UI
        docs = retriever.invoke(request.text)
        sources = [{"text": d.page_content, "ref": d.metadata["citation"]} for d in docs]
        
        return {
            "response": response,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/explain")
def explain_verse(request: ExplainRequest):
    """The 'Explainer' mode for specific verses."""
    try:
        # We don't need retrieval here as we are explaining a specific verse provided in text
        chain = (
            {"question": RunnablePassthrough(), "mode": lambda x: request.mode}
            | explain_prompt
            | llm
            | StrOutputParser()
        )
        response = chain.invoke(request.text)
        return {"response": response}
    except Exception as e:
        print(f"Error in explain_verse: {e}") # Log the error to console
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prayer")
def create_prayer(request: UserRequest):
    """The 'Prayer Architect': Formulates a prayer based on keywords."""
    try:
        chain = prayer_prompt | llm | StrOutputParser()
        prayer_text = chain.invoke({"topic": request.text})
        return {"prayer": prayer_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To start: uvicorn app.main:app --reload
