from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.merge import MergedDataLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

import config

"""Se crea una clase gestor para inicializar el modelo de IA, generar los embeddings
   y crear las pipelines con los prompts y lo anteriormente mencionado para poder 
   tener nuetro agente listo para poder responder las preguntas que se le realicen."""
class rag_gestor():
    def get_llm(self,llm_selection= None) -> ChatGoogleGenerativeAI | ChatGroq:
      if llm_selection == 'gemini':
        model = ChatGoogleGenerativeAI(
            api_key=os.environ['GEMINI_API_KEY'],
            model=config.GEMINI_MODEL,
            temperature=0.4
        )
      else:
        model = ChatGroq(
            api_key=os.environ['GROQ_API_KEY'],
            model_name=config.GROQ_MODEL,
            temperature=0.4
        )
  
      return model
   
    def data_loader(self,file_dir):
      docs = DirectoryLoader(file_dir, glob="*.pdf").load()
      return docs
  
  
    def data_splitter(self,docs) -> list:
      text_splitter = RecursiveCharacterTextSplitter(
          chunk_size=config.CHUNK_SIZE,
          chunk_overlap=config.CHUNK_OVERLAP,
          separators=["\n\n", "\n", ". ", " ", ""],
      )
      chunks = text_splitter.split_documents(docs)
      return chunks
  
    def get_embeddings(self,embedding_choice="free") -> HuggingFaceEmbeddings | GoogleGenerativeAIEmbeddings:
      # La generación del embedding la realizamos con hugginface para poder ahorrar
      # tokens que seran destinados a responder las consultas que se hagan a nuestro modelo.
      # De todas formas se deja el codigo para realizar embedings con gemini
      # en caso de que se desee probar como responderian el rag.
      if embedding_choice == "free":
        emb_model = HuggingFaceEmbeddings(model_name=config.HF_EMBEDDING_MODEL)
      else:
        emb_model = GoogleGenerativeAIEmbeddings(
            model=config.GEMINI_EMBEDDING_MODEL,
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            task_type="retrieval_document",  # optimizado para indexar documentos
        )
  
      return emb_model
      
    def generate_vector_store(self,chunks,embeddings) -> Chroma:
      if os.path.exists(config.PERSIST_DIR):
        vectordb = Chroma(
            persist_directory=config.PERSIST_DIR,
            embedding_function=embeddings,
        )
      else:
          vectordb = Chroma.from_documents(
              documents=chunks,
              embedding=embeddings,
              persist_directory=config.PERSIST_DIR,
          )
          vectordb.persist()
      return vectordb
  
    def format_docs(self,docs):
      return "\n\n".join(doc.page_content for doc in docs)
  
  
    def build_rag_chain(self, vectordb, llm):
        retriever = vectordb.as_retriever(search_kwargs={"k": 4})
  
        SYSTEM_PROMPT = """Sos el asistente interno de documentación técnica de Santo Pegasus, una empresa de tecnología especializada en el desarrollo de software escalable bajo arquitectura de microservicios y soluciones de Inteligencia Artificial (RAG). La empresa mantiene estándares técnicos rigurosos en ingeniería back-end y front-end, y prioriza la excelencia operativa y la seguridad en infraestructuras de nube.
  
        Tu función es responder consultas de empleados (desarrolladores, líderes técnicos, personal de onboarding y SRE) basándote EXCLUSIVAMENTE en el contenido de los siguientes documentos oficiales de la empresa:
  
        1. **arquitectura-microservicios-mapa-dominios.pdf** — Arquitectura general, catálogo de microservicios, dependencias entre servicios, patrones de comunicación, estrategia de bases de datos, API Gateway, infraestructura cloud, observabilidad, versionado de APIs, seguridad entre servicios, squads/ownership, roadmap técnico y ADRs.
  
        2. **Guía Oficial de Ingeniería Back-end** — Principios de ingeniería, patrones arquitectónicos (Java/Spring Boot), design patterns, implementación de IA y RAG, GitFlow, code review, seguridad, gestión de bases de datos y migrations, testing, CI/CD y deploy.
  
        3. **Guía Oficial de Ingeniería Front-end** — Filosofía front-end, principios de ingeniería, stack tecnológico, arquitectura de componentes, gestión de estado, consumo de APIs, estándares de código, design system, formularios, testing, code review, control de versiones, performance/Web Vitals, seguridad y CI/CD.
  
        4. **Manual de Onboarding para Nuevos Desarrolladores** — Cultura y bienvenida institucional, estructura del equipo, accesos del día 1, configuración de entorno local (back-end y front-end), Git, plan 30/60/90 días, herramientas internas, code review, beneficios y políticas de RRHH, seguridad, checklist de la semana 1, contactos útiles y FAQ.
  
        5. **Protocolo de Respuesta a Incidentes y Post-Mortems** — Filosofía SRE, clasificación de severidad, roles durante incidentes, detección y alertas, proceso de respuesta, rollback en Docker y AWS ECS, comunicación durante incidentes, criterios de cierre, plantilla de post-mortem, métricas SLI/SLO/SLA, error budget y GameDays.
  
        REGLAS DE RESPUESTA:
        - Respondé únicamente con información presente en el contexto recuperado. Si la respuesta no está en el contexto, decilo explícitamente: no inventes procedimientos, comandos, nombres de servicios, políticas ni datos de contacto.
        - Cuando sea posible, indicá de qué documento proviene la información (por ejemplo: "Según la Guía de Ingeniería Back-end...").
        - Usá un tono profesional, técnico y directo, acorde a los estándares de ingeniería de la empresa. Evitá informalidades excesivas.
        - Si la consulta involucra información sensible (credenciales, accesos, datos de RRHH, contactos personales), respondé solo con lo que el documento indica como público/interno general, sin asumir permisos del usuario.
        - Si una pregunta cruza varios documentos (ej: un incidente que requiere revisar arquitectura y protocolo de incidentes), integrá la información de todas las fuentes relevantes de forma clara y estructurada.
        - No emitas opiniones personales sobre decisiones técnicas de la empresa (ADRs, stack elegido, etc.); limitate a explicar lo que el documento establece.
        - Si el usuario pregunta algo fuera del alcance de estos documentos (temas generales de programación no cubiertos, noticias, etc.), aclará que tu conocimiento se limita a la documentación interna de la empresa.
  
        Contexto recuperado:
        {context}
  
        Pregunta del usuario: {question}
  
        Respuesta:"""
  
        prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
  
        chain = (
            {"context": retriever | self.format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain