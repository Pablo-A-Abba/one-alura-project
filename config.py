import argparse
import os


_PDF_DIR_NAME = "santos_pegasus_files"
_PERSIST_DIR_NAME = "chroma_db"
_IMG_NAME = "pegasus_icon.svg"

PDF_DIR = os.path.join(os.getcwd(), _PDF_DIR_NAME)
PERSIST_DIR = os.path.join(os.getcwd(), _PERSIST_DIR_NAME)
IMG_PATH = os.path.join(os.getcwd(), "image", _IMG_NAME)

HF_EMBEDDING_MODEL = "BAAI/bge-m3"
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_MODEL = "gemini-2.5-flash"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

"""Obtiene los argumentos dados en el comando de ejecucion"""
def get_options() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", type=str, required=False)
    parser.add_argument("--emb", type=str, required=False)
    parser.add_argument("--allgem", action="store_true", required=False)

    args = parser.parse_args()

    llm = None
    emb = None

    if args.allgem:
        llm = "gemini"
        emb = "gemini" 
    elif args.llm:
        llm = args.llm
        assert llm=="gemini", "La aplicacion no tiene habilitada esta opcion de llm."
    elif args.emb:
        emb = args.emb
        assert emb=="gemini", "La aplicacion no tiene habilitada esta opcion de embedding."

    return {"llm":llm,"emb":emb}   