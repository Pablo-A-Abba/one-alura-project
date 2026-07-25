import argparse

PDF_DIR = "/workspaces/one-alura-project/santos_pegasus_files/"   # carpeta se encuentran los pdfs de la empresa
PERSIST_DIR = "/chroma_db"     # directorio necesario para tener persistencia de la vector store
HF_EMBEDDING_MODEL = "BAAI/bge-m3"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.5-flash"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

def get_options() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", type=str, required=False)
    parser.add_argument("--emb", type=str, required=False)
    parser.add_argument("--allgem", type=bool, required=False)

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
    