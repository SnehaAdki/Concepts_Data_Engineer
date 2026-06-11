import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate



def load_document(file_path: str):
   ext = os.path.splitext(file_path)[1].lower()
   loaders = {".txt": TextLoader, ".pdf": PyPDFLoader, ".docx": Docx2txtLoader}
   loader_cls = loaders.get(ext)
   if loader_cls is None:
       raise ValueError(f"Unsupported file type: {ext}")
   return loader_cls(file_path).load()




def build_vector_store(documents):
   splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
   chunks = splitter.split_documents(documents)
   embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
   return Chroma.from_documents(
       documents=chunks, embedding=embeddings, persist_directory="./chroma_db_company"
   )




def ask(vector_store, question: str) -> str:
   """RAG pipeline built manually — no langchain.chains needed."""
   # 1. Retrieve relevant chunks
   retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
   docs = retriever.invoke(question)


   # 2. Build context from retrieved docs
   context = "\n\n".join(doc.page_content for doc in docs)


   # 3. Build prompt
   prompt = ChatPromptTemplate.from_template(
       "Use the following context to answer the question. "
       "If the answer is not in the context, say 'I don't have enough information.'\n\n"
       "Context:\n{context}\n\n"
       "Question: {question}\n\n"
       "Answer:"
   )


   # 4. Call LLM
   llm = ChatOllama(model="gemma3:1b", temperature=0.3)
   chain = prompt | llm  # simple LCEL pipe
   result = chain.invoke({"context": context, "question": question})


   # 5. Format output
   sources = {doc.metadata.get("source", "unknown") for doc in docs}
   return f"Answer: {result.content}\n\nSources: {', '.join(sources)}"


doc_path = "/Users/SAI15/Desktop/Concepts/RAG/Company.txt"
documents = load_document(doc_path)

print(f"Loaded {len(documents)} page(s)")


vector_store = build_vector_store(documents)
print("Vector store built.")


print(ask(vector_store, "How many employee are their?"))
