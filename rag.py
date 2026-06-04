import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

os.environ["PATH"] = os.environ["PATH"] + ";C:\\ffmpeg\\bin"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def build_vector_store(segments):
    print("Building vector store...")
    texts = []
    for seg in segments:
        minutes = int(seg["start"] // 60)
        seconds = int(seg["start"] % 60)
        texts.append(f"[{minutes:02d}:{seconds:02d}] {seg['text']}")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(texts)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    
    db = Chroma.from_documents(docs, embeddings, persist_directory="chroma_db")
    print("Vector store built successfully!")
    return db

def ask_question(question, segments):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    
    docs = db.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    
    prompt = f"""Based on the following video transcript excerpts, answer the question.
Always mention the timestamp when referencing specific parts.

Transcript excerpts:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    with open("transcript.json", "r") as f:
        segments = json.load(f)
    
    build_vector_store(segments)
    
    answer = ask_question("what is the main message of this video?", segments)
    print("\nQuestion: what is the main message of this video?")
    print(f"Answer: {answer}")