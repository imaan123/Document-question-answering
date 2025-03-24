**Private Document Chat App (Flask + LangChain + Ollama)**

- This is a lightweight Flask-based web application that allows you to chat with your private PDF documents using local LLMs and retrieval-augmented generation (RAG) with LangChain.

🚀 **Features**

- Upload and chat with multiple PDF documents.

- All data processed locally using Ollama and FAISS — no data leaves your machine.

- Session management with auto-timeout for security.

- Simple and intuitive frontend interface.

🛠️ **Tech Stack**

- Flask: Web framework.

- LangChain: Document processing, embeddings, vector search, RAG.

- Ollama: Local LLM (Here we have used Gemma-1b).

- FAISS: Local vector store for document embeddings.

- HuggingFace Embeddings: all-MiniLM-L6-v2.

⚙️ **Setup Instructions**

- Install Dependencies
```console
pip install requirements.txt
```

- Start Ollama (if not already running)
```console
ollama serve
```

- Run the Flask App
```console
flask run
```

- Access the App
Open your browser at: http://127.0.0.1:5000