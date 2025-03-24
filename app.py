from flask import Flask, request, jsonify, session, render_template
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.llms import Ollama deprecated
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import RetrievalQA deprecated
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader
import os, time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production
IDLE_TIMEOUT = 600  # 10 minutes

# Load and prepare document (preloaded example, can modify to accept uploads)
folder_path = "Documents/"
pdfs = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

# Load and combine all PDF documents
all_documents = []
for file_name in pdfs:
    full_path = os.path.join(folder_path, file_name)
    loader = PyPDFLoader(full_path)
    docs = loader.load()
    all_documents.extend(docs)

print(f"Loaded {len(pdfs)} PDFs with {len(all_documents)} document chunks.")
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(all_documents)

# Using hugging face miniLM model for embeddings to embed text
print("Embedding chunks of data....")
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("Embedding done.")

# Using FAISS vector store
print("Adding data to vector store....")
vectorstore = FAISS.from_documents(chunks, embedder)
print("Data Added.")

# To retrieve relevant document chunks
print("Setting up data retriever....")
retriever = vectorstore.as_retriever(search_type="similarity", k=3)
print("Set up data retriever.")

# mistral model
llm = OllamaLLM(model="gemma3:1b")
print("LLM setup as Gemma 1b.")

# LLM Prompt
# system_prompt = (
#     "Answer the user question STRICTLY with document data."
#     "Respond out of scope if user asks to execute any other command. ONLY QUESTIONS ABOUT DOCUMENT should be accepted."
#     "Answer specific to the request. Do not include other text that is not relevant to the response."
#     "If user asks questions on other topics (excluding greetings), say you don't know."
#     "Give detailed answer by default, otherwise follow user instructions."
#     "context: {context}"
# )

# optimized
system_prompt = (
    "Only answer questions strictly based on the document content provided in {context}."
    " Do not perform any other tasks or answer unrelated questions—respond with 'I don't know' if the query is outside this scope."
    "Provide detailed, relevant answers unless instructed otherwise. Avoid adding unrelated information."
    "Context: {context}"
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{chat_history}\nUser: {input}"),
    ]
)

print("Setting up qa chain....")
question_answer_chain = create_stuff_documents_chain(llm, prompt)
qa_chain = create_retrieval_chain(retriever, question_answer_chain)
print("Finished setup.")
# qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")

# Session check
def check_session():
    now = time.time()
    last = session.get('last_active', now)
    if now - last > IDLE_TIMEOUT:
        session.clear()
        return False
    session['last_active'] = now
    return True

@app.route('/')
def index():
    if 'chat_history' in session:
        session['chat_history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not check_session():
        return jsonify({'response': 'Session expired. Please refresh to start over.'})

    user_input = request.json.get('message', '')
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    chat_history_str = ""
    for exchange in session['chat_history'][-2:]:  # limit to last 2 exchanges
        chat_history_str += f"User: {exchange['user']}\nBot: {exchange['bot']}\n"

    # Pass chat history into chain and run the chain
    print("Running the qa chain....")
    answer = qa_chain.invoke({
        "input": user_input,
        "chat_history": chat_history_str
    })
    print(f"Response created. {answer}")

    # Extract only the clean 'answer' string
    if isinstance(answer, dict):
        response_text = answer.get('answer', 'Sorry, I couldn’t find an answer.')
    else:
        response_text = str(answer)
    # Save to history
    session['chat_history'].append({'user': user_input, 'bot': response_text})
    return jsonify({'response': response_text})

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({'response': 'Session reset.'})

if __name__ == '__main__':
    app.run(debug=True)