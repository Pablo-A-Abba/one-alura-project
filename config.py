from google.colab import userdata
import os
os.environ['GROQ_API_KEY'] = userdata.get('GROQ_API_KEY')
os.environ['GEMINI_API_KEY'] = userdata.get('GEMINI_API_KEY')

PDF_DIR = "./santos_pegasus_files/"   # carpeta se encuentran los pdfs de la empresa
PERSIST_DIR = "./chroma_db"     # directorio necesario para tener persistencia de la vector store
HF_EMBEDDING_MODEL = "BAAI/bge-m3"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.5-flash"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150