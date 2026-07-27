from rag import rag_gestor
import streamlit as st
import config

@st.cache_resource(show_spinner=False)
def build_pipeline(options:dict):
    """Arma el pipeline completo del RAG: carga documentos, genera embeddings,
    construye el vector store y prepara la chain lista para responder consultas.

    Decorado con @st.cache_resource para que se ejecute una sola vez por proceso,
    incluso a través de múltiples reruns de Streamlit."""
    rag_gen = rag_gestor()

    documents = rag_gen.data_loader(config.PDF_DIR)
    chunks = rag_gen.data_splitter(documents)
    embeddings = rag_gen.get_embeddings(options['emb'])
    vectordb = rag_gen.generate_vector_store(chunks, embeddings)
    llm = rag_gen.get_llm(options['llm'])
    rag_chain = rag_gen.build_rag_chain(vectordb, llm)

    return rag_chain


def streamlit_page(options:dict):
    st.set_page_config(page_title="Asistente de Documentación Técnica | Santo Pegasus", layout="centered")
    st.image(config.IMG_PATH, width=120)
    st.title("Asistente de Documentación Técnica — Santo Pegasus")
    

    st.info("""
    Este asistente responde consultas técnicas basándose **exclusivamente** en la documentación
    oficial interna de Santo Pegasus. Está pensado para desarrolladores, líderes técnicos,
    personal en onboarding y equipos de SRE.

    Podés preguntar sobre:

    * 🏗️ **Arquitectura de microservicios**: catálogo de servicios, dependencias, patrones de
      comunicación, API Gateway, estrategia de bases de datos, seguridad entre servicios y ADRs.
    * ⚙️ **Ingeniería Back-end**: patrones arquitectónicos, implementación de IA/RAG, GitFlow,
      testing, CI/CD y gestión de bases de datos.
    * 🎨 **Ingeniería Front-end**: stack tecnológico, arquitectura de componentes, design system,
      performance y estándares de código.
    * 🚀 **Onboarding**: accesos, configuración de entorno local, plan 30/60/90 días y checklist
      de la primera semana.
    * 🚨 **Respuesta a incidentes**: clasificación de severidad, rollback, comunicación durante
      incidentes y post-mortems.

    Las respuestas se generan únicamente a partir del contenido de estos documentos — si algo
    no está cubierto, el asistente te lo va a indicar en vez de inventar una respuesta.
    """)

    st.markdown("---")
    st.markdown("## 💬 Consultá la documentación interna")

    question = st.text_input(
        "Escribí tu consulta (ej: '¿Cuál es el proceso de rollback en incidentes de severidad alta?')"
    )

    if st.button("Responder", key="responder_pregunta"):
        if not question.strip():
            st.warning("Escribí una pregunta antes de enviar.")
        else:
            # El pipeline se construye recién cuando se envía la primera consulta,
            # y queda cacheado (@st.cache_resource) para las siguientes preguntas.
            if "rag_chain" not in st.session_state:
                with st.spinner("Inicializando el asistente por primera vez: cargando documentos y generando embeddings... esto puede tardar unos segundos."):
                    st.session_state.rag_chain = build_pipeline(options)

            with st.spinner("Buscando en la documentación 🦜"):
                response = st.session_state.rag_chain.invoke(question)
                st.markdown("### Respuesta")
                st.markdown(response)


if __name__ == "__main__":
    options = config.get_options()
    streamlit_page(options)