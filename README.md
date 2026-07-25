# Asistente de Documentación Técnica — Santo Pegasus

Asistente conversacional basado en RAG (Retrieval-Augmented Generation) que responde consultas de empleados de **Santo Pegasus** —una empresa ficticia de tecnología especializada en microservicios e IA— basándose exclusivamente en su documentación interna oficial.

El asistente está pensado para desarrolladores, líderes técnicos, personal en proceso de onboarding y equipos de SRE, y responde únicamente con información presente en los documentos indexados, evitando inventar procedimientos, comandos o datos que no estén respaldados por las fuentes oficiales.

## 📄 Documentos que utiliza el asistente

1. **Arquitectura de Microservicios y Mapa de Dominios** — catálogo de servicios, dependencias, patrones de comunicación, API Gateway, estrategia de bases de datos, seguridad y ADRs.
2. **Guía Oficial de Ingeniería Back-end** — patrones arquitectónicos, implementación de IA/RAG, GitFlow, testing, CI/CD.
3. **Guía Oficial de Ingeniería Front-end** — stack tecnológico, arquitectura de componentes, design system, performance.
4. **Manual de Onboarding para Nuevos Desarrolladores** — accesos, configuración de entorno, plan 30/60/90 días.
5. **Protocolo de Respuesta a Incidentes y Post-Mortems** — clasificación de severidad, rollback, comunicación, SLI/SLO/SLA.

---

## 🏗️ Arquitectura de la solución

El flujo del sistema sigue el patrón clásico de RAG (Retrieval-Augmented Generation):

```
PDFs (santos_pegasus_files/)
        │
        ▼
 ┌───────────────┐
 │  Data Loader  │   PyPDFLoader (langchain_community)
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │ Text Splitter │   RecursiveCharacterTextSplitter
 └───────┬───────┘   (chunk_size=1000, overlap=150)
         ▼
 ┌───────────────┐
 │   Embeddings  │   HuggingFace (BAAI/bge-m3, local, gratis)
 │               │   o Gemini (gemini-embedding-001, API)
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │  Vector Store │   Chroma (persistido en disco)
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │   Retriever   │   Búsqueda por similitud (k=4)
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │  Prompt + LLM │   Groq (Llama 3.3 70B) o Gemini 2.5 Flash
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │  Output Parser│   StrOutputParser
 └───────┬───────┘
         ▼
   Respuesta al usuario
```

**Componentes principales del código:**

- **`rag.py`** — clase `rag_gestor` que centraliza toda la lógica: carga de documentos, splitting, generación de embeddings, construcción del vector store y armado de la chain con el prompt del sistema.
- **`config.py`** — configuración centralizada: paths de datos, modelos de LLM/embeddings, parámetros de chunking, y manejo de argumentos de línea de comandos (`--llm`, `--emb`, `--allgem`).
- **`app.py`** — interfaz web con Streamlit.
- **`cli.py`** — interfaz de consola, para testing rápido sin levantar la UI.

Ambas interfaces (`app.py` y `cli.py`) consumen la misma clase `rag_gestor`, por lo que cualquier cambio en la lógica del RAG se refleja automáticamente en las dos.

---

## 🛠️ Tecnologías y herramientas utilizadas

| Categoría | Herramienta |
|---|---|
| Orquestación LLM | [LangChain](https://www.langchain.com/) (`langchain`, `langchain-core`, `langchain-community`, `langchain-text-splitters`) |
| Modelo de lenguaje (LLM) | [Groq](https://groq.com/) (`llama-3.3-70b-versatile`) o [Google Gemini](https://ai.google.dev/) (`gemini-2.5-flash`) |
| Embeddings | [Hugging Face Sentence Transformers](https://www.sbert.net/) (`BAAI/bge-m3`, local) y/o Google Gemini (`gemini-embedding-001`, API) |
| Vector store | [Chroma](https://www.trychroma.com/) vía `langchain-chroma` |
| Interfaz web | [Streamlit](https://streamlit.io/) |
| Carga de PDFs | `PyPDFLoader` (`langchain_community`) |
| Gestión de variables de entorno | `python-dotenv` |
| Lenguaje | Python 3.13 |

---

## ⚙️ Instrucciones para ejecutar el proyecto

### 1. Requisitos previos

- Python 3.13 instalado.
- Una clave de API de [Groq](https://console.groq.com/) y/o de [Google AI Studio](https://aistudio.google.com/) (Gemini), según qué proveedor pienses usar.
- (Opcional) Un token de [Hugging Face](https://huggingface.co/settings/tokens) si vas a usar el modelo de embeddings gratuito.

### 2. Clonar el repositorio e instalar dependencias

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Creá un archivo `.env` en la raíz del proyecto con tus credenciales:

```env
GROQ_API_KEY=tu_api_key_de_groq
GEMINI_API_KEY=tu_api_key_de_gemini
HF_TOKEN=tu_token_de_huggingface
```

### 4. Agregar los documentos

Colocá los PDFs de la documentación interna dentro de la carpeta configurada en `config.py` (`santos_pegasus_files/` por defecto).

### 5. Ejecutar el asistente

**Modo consola (CLI):**
```bash
python cli.py
```

**Modo web (Streamlit):**
```bash
streamlit run app.py
```

### 6. Opciones de línea de comandos

El proyecto permite elegir qué proveedor usar para el LLM y los embeddings mediante argumentos:

**Modo consola (CLI):**
```bash
# Usar Gemini tanto para el LLM como para los embeddings
python cli.py --allgem true

# Usar Gemini solo como LLM (embeddings quedan en modo gratuito/local)
python cli.py --llm gemini

# Usar Gemini solo para embeddings (LLM queda en Groq)
python cli.py --emb gemini
```

**Modo web (Streamlit):**
```bash
# Usar Gemini tanto para el LLM como para los embeddings
streamlit run app.py -- --allgem

# Usar Gemini solo como LLM (embeddings quedan en modo gratuito/local)

streamlit run app.py -- --llm gemini

# Usar Gemini solo para embeddings (LLM queda en Groq)
streamlit run app.py -- --emb gemini
```

Si no se pasa ningún argumento, el sistema usa por defecto **Groq** como LLM y **Hugging Face (local, gratuito)** para los embeddings.

---

## 💬 Ejemplos de preguntas que el agente puede responder

- "¿Cuáles son los pasos para hacer un rollback en un incidente de severidad alta?"
- "¿Qué patrones arquitectónicos se usan en el back-end con Spring Boot?"
- "¿Cómo configuro mi entorno local de desarrollo el primer día?"
- "¿Qué servicios dependen del API Gateway según el mapa de dominios?"
- "¿Cuál es el proceso de code review según la guía de ingeniería front-end?"
- "¿Qué información se registra en un post-mortem después de un incidente?"
- "¿Cuáles son los criterios para clasificar la severidad de un incidente?"
- "¿Qué debo hacer en mi primera semana según el manual de onboarding?"

---

## 🧪 Ejemplos de respuestas generadas por el agente

> _Sección a completar con capturas o transcripciones reales de la aplicación en funcionamiento._

**Pregunta:**
```
[completar]
```

**Respuesta:**
```
[completar]
```

---

**Pregunta:**
```
[completar]
```

**Respuesta:**
```
[completar]
```