from rag import rag_gestor
import config


def main(options:dict):
    rag_gen = rag_gestor()

    print("Cargando documentos...")
    documents = rag_gen.data_loader(config.PDF_DIR)
    print(f"  {len(documents)} elementos cargados.")

    print("Dividiendo en chunks...")
    chunks = rag_gen.data_splitter(documents)
    print(f"  {len(chunks)} chunks generados.")

    print("Generando/cargando embeddings...")
    embeddings = rag_gen.get_embeddings(options['emb'])

    print("Construyendo vector store...")
    vectordb = rag_gen.generate_vector_store(chunks, embeddings)

    print("Inicializando LLM...")
    llm = rag_gen.get_llm(options['llm'])

    rag_chain = rag_gen.build_rag_chain(vectordb, llm)

    print("\nAsistente de Documentación Técnica - Santo Pegasus")
    print("Escribí 'salir' para terminar.\n")

    while True:
        question = input("Pregunta: ")
        if question.strip().lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break
        if not question.strip():
            continue

        answer = rag_chain.invoke(question)
        print(f"\nRespuesta: {answer}\n")


if __name__ == "__main__":
    options = config.get_options()
    main(options)