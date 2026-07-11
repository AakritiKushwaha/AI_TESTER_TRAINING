import collections
import collections.abc
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import List

for name in ('Mapping', 'MutableMapping', 'Sequence', 'MutableSequence', 'Set', 'MutableSet', 'Callable'):
    if not hasattr(collections, name):
        setattr(collections, name, getattr(collections.abc, name))

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

import chromadb
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
CHROMA_DIR = BASE_DIR / 'chroma_data'
COLLECTION_NAME = 'prd_chunks'

app = FastAPI(title='Basic RAG Explorer')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
model = SentenceTransformer('all-MiniLM-L6-v2')


class QueryRequest(BaseModel):
    query: str


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    normalized = re.sub(r'\s+', ' ', text).strip()
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        if end >= len(normalized):
            chunks.append(normalized[start:])
            break
        split = normalized.rfind('.', start, end)
        if split == -1 or split <= start:
            split = end
        else:
            split += 1
        chunks.append(normalized[start:split].strip())
        start = max(start + chunk_size - overlap, split)
    return chunks


def load_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or '' for page in reader.pages]
    return '\n'.join(pages), len(reader.pages)


def ensure_collection():
    try:
        return client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return client.create_collection(name=COLLECTION_NAME)


def get_first_pdf() -> Path:
    pdfs = sorted(DATA_DIR.glob('*'))
    if not pdfs:
        raise HTTPException(status_code=404, detail='No file found in data folder')
    return pdfs[0]


def do_ingest(file_path: Path):
    if not file_path.exists():
        raise HTTPException(status_code=404, detail='File not found')

    text, page_count = load_pdf_text(file_path)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail='No text could be extracted from the file')

    embeddings = model.encode(chunks, show_progress_bar=False).tolist()
    dims = len(embeddings[0]) if embeddings else 0

    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME)
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f'chunk-{i}' for i in range(len(chunks))],
    )

    sample = embeddings[0][:8] if embeddings else []

    chunk_list = [
        {'index': i, 'chars': len(c), 'text': c}
        for i, c in enumerate(chunks)
    ]

    return {
        'message': 'File ingested successfully into local ChromaDB.',
        'file': file_path.name,
        'pages': page_count,
        'chunks': chunk_list,
        'embeddings': {
            'total': len(embeddings),
            'dims': dims,
            'sample': sample,
        },
        'collection': COLLECTION_NAME,
    }


@app.post('/api/ingest')
def ingest_pdf():
    pdf_path = get_first_pdf()
    return do_ingest(pdf_path)


@app.post('/api/ingest_file')
async def ingest_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail='No file provided')

    ext = Path(file.filename).suffix.lower()
    if ext not in ('.pdf', '.txt', '.md'):
        raise HTTPException(status_code=400, detail='Only PDF, .txt, and .md files are accepted')

    dest = DATA_DIR / file.filename
    with open(dest, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    return do_ingest(dest)


@app.post('/api/reset')
def reset_index():
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    return {'message': 'Index reset successfully.'}


@app.post('/api/suggestions')
def get_suggestions():
    collection = ensure_collection()
    if collection.count() == 0:
        return {'suggestions': ['What does this document cover?']}
    all_data = collection.get()
    chunks = all_data.get('documents', [])
    if not chunks:
        return {'suggestions': ['What does this document cover?']}
    preview = '\n'.join(chunks[:3])
    try:
        api_key = os.getenv('GROQ_API_KEY')
        body = json.dumps({
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'Based on the document excerpt below, generate exactly 4 concise '
                        'questions a user would want to ask about this document. '
                        'Reply with a JSON array of strings only, no other text.'
                    )
                },
                {'role': 'user', 'content': f'Excerpt:\n{preview[:1500]}'}
            ],
            'temperature': 0.3,
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.groq.com/openai/v1/chat/completions',
            data=body,
            headers={
                'Authorization': f"Bearer {api_key}",
                'Content-Type': 'application/json',
                'User-Agent': 'BasicRAGExplorer/1.0',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        raw = payload['choices'][0]['message']['content']
        import ast
        suggestions = ast.literal_eval(raw)
        if not isinstance(suggestions, list) or len(suggestions) != 4:
            raise ValueError('Unexpected format')
    except Exception:
        suggestions = ['What does this document cover?', 'What are the key features?', 'What are the requirements?', 'What topics are discussed?']
    return {'suggestions': suggestions}


@app.post('/api/query')
def query_pdf(payload: QueryRequest):
    collection = ensure_collection()
    if collection.count() == 0:
        raise HTTPException(status_code=400, detail='The index is empty. Run ingestion first.')

    query_embedding = model.encode(payload.query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=4)

    documents = results.get('documents', [[]])[0]
    if not documents:
        raise HTTPException(status_code=404, detail='No relevant chunks found')

    model_name = 'llama-3.3-70b-versatile'

    context_parts = []
    for i, doc in enumerate(documents):
        context_parts.append(f'【Chunk {i+1}】 {doc}')
    context = '\n\n'.join(context_parts)

    try:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise RuntimeError('GROQ_API_KEY is not set')
        body = json.dumps({
            'model': model_name,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'You answer using only the provided context. '
                        'Cite the chunk each piece of information comes from '
                        'by placing the chunk marker inline, e.g. 【Chunk 3】. '
                        'If the answer is not in the context, say so clearly.'
                    )
                },
                {
                    'role': 'user',
                    'content': f'Query: {payload.query}\n\nContext:\n{context}'
                }
            ],
            'temperature': 0.2,
        }).encode('utf-8')
        request = urllib.request.Request(
            'https://api.groq.com/openai/v1/chat/completions',
            data=body,
            headers={
                'Authorization': f"Bearer {api_key}",
                'Content-Type': 'application/json',
                'User-Agent': 'BasicRAGExplorer/1.0',
            },
            method='POST'
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload_json = json.loads(response.read().decode('utf-8'))
        answer = payload_json['choices'][0]['message']['content']
        usage = payload_json.get('usage', {})
    except Exception as e:
        print(f'Groq API error: {e}', flush=True)
        answer = 'Unable to reach the Groq API. Showing the retrieved context instead.\n\n' + context
        usage = {}

    return {
        'answer': answer,
        'model': model_name,
        'usage': {
            'prompt_tokens': usage.get('prompt_tokens', 0),
            'completion_tokens': usage.get('completion_tokens', 0),
            'total_tokens': usage.get('total_tokens', 0),
        },
        'sources': documents,
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend:app', host='127.0.0.1', port=8000, reload=True)
