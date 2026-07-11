**RAG Explorer — Project Prompt**

I want you to build a simple RAG (Retrieval-Augmented Generation) Explorer as a lightweight React + Vite web application.

**Data Source**
- A PDF file will be provided in the `/data` folder — it's a Product Requirements Document (PRD) for VWO.com.

**Ingestion Pipeline**
1. Read and chunk the PDF stored in `/data`.
2. Use the **Nomic Embedding Model** to generate embeddings for each chunk.
3. Set up **ChromaDB in embedded/persistent client mode** — no separate ChromaDB server or Docker container. Use ChromaDB's local persistent client, storing all data on-disk in a local folder (e.g., `./chroma_data`). Store the chunked embeddings there.

**Retrieval & Query Flow**
- When the user submits a query related to the PDF:
  1. Retrieve the **top 4 most relevant chunks** from the local ChromaDB instance based on the query.
  2. Display these top 4 chunks in the UI so the retrieval process is visible/transparent.
  3. Pass the retrieved chunks along with the query to **Groq's API**, using the **GPT-OSS 120B** model, to generate the final answer.

**UI Requirements**
- Build a simple, clean interface (React + Vite) that visually showcases the full RAG pipeline:
  - PDF ingestion → chunking → embedding → storage in local ChromaDB → query → retrieval of top 4 chunks → final LLM-generated answer.
- The goal is to make the RAG mechanism transparent and explorable, not just a black-box chatbot.

**Tech Stack Summary**
| Component | Tool |
|---|---|
| Frontend | React + Vite |
| Embedding Model | Nomic Embed |
| Vector Store | ChromaDB — embedded/persistent client, on-disk, no separate server |
| LLM Provider | Groq API |
| LLM Model | GPT-OSS 120B |

**Constraints**
- No cloud-hosted vector database, no ChromaDB Cloud, no separate ChromaDB server process.
- All embeddings and chunks stay on-disk locally in embedded/persistent client mode.