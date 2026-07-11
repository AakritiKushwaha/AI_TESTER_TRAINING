# RAG Explorer — Project Prompt

Build a simple RAG (Retrieval-Augmented Generation) Explorer as a lightweight React + Vite web application. The goal is to make the RAG mechanism transparent and explorable, not just a black-box chatbot.

## Data Source
- A PDF file will be provided in the `/data` folder — it's a Product Requirements Document (PRD) for VWO.com.

## Ingestion Pipeline
1. Read and chunk the PDF stored in `/data`.
2. Use the **Nomic Embedding Model** to generate embeddings for each chunk.
3. Set up **ChromaDB in embedded/persistent client mode** — no separate ChromaDB server or Docker container. Use ChromaDB's local persistent client, storing all data on-disk in a local folder (e.g., `./chroma_data`). Store the chunked embeddings there.

## Retrieval & Query Flow
When the user submits a query related to the PDF:
1. Retrieve the **top 4 most relevant chunks** from the local ChromaDB instance based on the query.
2. Display these top 4 chunks in the UI so the retrieval process is visible/transparent.
3. Pass the retrieved chunks along with the query to **Groq's API**, using the **GPT-OSS 120B** model, to generate the final answer.

## Tech Stack Summary
| Component | Tool |
|---|---|
| Frontend | React + Vite |
| Embedding Model | Nomic Embed |
| Vector Store | ChromaDB — embedded/persistent client, on-disk, no separate server |
| LLM Provider | Groq API |
| LLM Model | GPT-OSS 120B |

## Constraints
- No cloud-hosted vector database, no ChromaDB Cloud, no separate ChromaDB server process.
- All embeddings and chunks stay on-disk locally in embedded/persistent client mode.

## UI Requirements

**Layout**
- Two-column layout: left column for ingestion controls, right column for the ask/answer panel.
- At the top of the page, show a horizontal pipeline stepper with 6 numbered stages (1. PDF, 2. Chunk, 3. Embed, 4. Store, 5. Retrieve, 6. Answer), each as a badge with a short label, connected by arrows.

**Ingestion panel (left)**
- An "Ingest folder" button that reads a hardcoded source folder path (displayed as text), plus a "Reset" button.
- A drag-and-drop zone below it as an alternative: "Drop a PDF, .txt or .md here — or click to browse". Uploading a file here replaces the current index.
- After ingestion, show 4 stat cards: Pages, Chunks, Embed dims, Stored count.
- Show a "Sample embedding" preview — the first 8 dimensions of one embedding vector, as raw numbers.
- Show a "Chunk preview" list with each chunk's index and character count, expandable to view full text.

**Ask panel (right)**
- Query textarea with an "Ask" button.
- Row of clickable suggested-question chips above the textarea (e.g., generated from the PDF's likely topics) that populate the textarea on click.
- Answer section header shows the model name and token count used for that response.
- Inline citation markers (e.g., 【Chunk 1】) embedded directly next to each claim in the answer text, not just listed separately as sources.

**Styling**
- Dark theme with orange/amber accent color for buttons, badges, and highlights (instead of blue/purple).