from rag import rag_gestor
import config

def main():
    llm = rag_gestor()
    print("Cargando documentos...")
    documents = llm.data_loader(config.PDF_DIR)
    print(f"  {len(documents)} elementos cargados.")

    print("Dividiendo en chunks...")
    chunks = llm.data_splitter(documents)
    print(f"  {len(chunks)} chunks generados.")

    print("Generando/cargando embeddings...")
    embeddings = llm.get_embeddings()

    print("Construyendo vector store...")
    vectordb = llm.generate_vector_store(chunks, embeddings)

    print("Inicializando LLM...")
    llm = llm.get_llm()

    rag_chain = llm.build_rag_chain(vectordb, llm)

    print("\nRAG listo. Escribí 'salir' para terminar.\n")
    while True:
        question = input("Pregunta: ")
        if question.strip().lower() in ("salir", "exit", "quit"):
            break
        answer = rag_chain.invoke(question)
        print(f"\nRespuesta: {answer}\n")


if __name__ == "__main__":
    main()