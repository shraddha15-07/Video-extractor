# 🎬 Video Note Extractor

An AI-powered web app that converts any YouTube video into 
organized study notes automatically.

## ✨ Features
- 📝 Organized notes with headings and bullet points
- ⏱️ Key timestamps of important moments  
- ✅ Action items extracted automatically
- 💬 Q&A — ask any question about the video
- 📄 Full transcript with every timestamp
- ⬇️ Download notes as Markdown file

## 🛠️ Tech Stack
| Tool | Purpose |
|------|---------|
| yt-dlp | Download YouTube audio |
| Whisper | Speech to text |
| Groq + LLaMA 3 | AI note generation |
| LangChain | Text splitting |
| ChromaDB | Vector database for Q&A |
| sentence-transformers | Text embeddings |
| Streamlit | Web interface |

## 🚀 How to Run
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install packages: `pip install -r requirements.txt`
5. Create `.env` file and add: `GROQ_API_KEY=your_key_here`
6. Run: `streamlit run app.py`

## 📸 Demo
[Add screenshot of your app here]

## 👤 Built by
Shraddha — built from scratch as an AI project