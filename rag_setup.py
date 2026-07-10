from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os


pdf_folder = "data/pdfs"
all_documents = []

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        filepath = os.path.join(pdf_folder, filename)
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        all_documents.extend(pages)
        print(f"Loaded {filename} — {len(pages)} pages")

print(f"\nTotal pages loaded: {len(all_documents)}")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,       
    chunk_overlap=100,    
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = text_splitter.split_documents(all_documents)
print(f"Total chunks created: {len(chunks)}")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db"   
)

print("\nVector store created and saved to 'chroma_db/' folder!")
