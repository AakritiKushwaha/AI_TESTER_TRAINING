# AI Tester Training

This workspace contains a collection of AI-assisted testing projects designed for hands-on learning, automation practice, and experimentation with modern test engineering tools.

## Projects Included

### 1. API Contract Validator with Langflow UI
Location: [API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW](API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW)

A React + Vite application that validates API contracts using JSON schemas and an AI-powered Langflow backend.

### 2. REST Assured API Testing Framework
Location: [RESTASSURED_PROJECT_USING_AI](RESTASSURED_PROJECT_USING_AI)

A Java-based API automation framework built with REST Assured, TestNG, and supporting libraries.

### 3. Basic RAG Explorer
Location: [RAGs/BASIC RAG](RAGs/BASIC%20RAG)

A lightweight RAG web app built with React + Vite and FastAPI. Ingests PDFs, embeds with all-MiniLM-L6-v2, stores in ChromaDB, and answers questions via Groq LLM. All local, no cloud dependencies.

### 4. Langflow Naive RAG with RAG Explorer UI (New!)
Location: [RAGs/LANGFLOW_NAIVE_RAG_WITH_RAG_EXPLORER_UI](RAGs/LANGFLOW_NAIVE_RAG_WITH_RAG_EXPLORER_UI)

Same RAG Explorer interface but with a Langflow-powered backend. Uses Langflow (ChromaDB + Mistral Embeddings + Groq LLM) as the orchestration engine instead of inline Python code. The FastAPI backend is a thin proxy to Langflow's REST API. Deployed on Vercel with ngrok-exposed Langflow. Ingested 1,000 e-commerce test cases across 10 modules.

### 5. Advanced RAG Explorer
Location: [RAGs/ADVANCE_RAG](RAGs/ADVANCE_RAG)

An end-to-end Advanced Retrieval-Augmented Generation application that ingests 5,000 VWO test cases, indexes them with hybrid (dense + sparse) vectors in Qdrant, and answers questions using a multi-stage pipeline with LLM generation.

### 6. Test Strategy Builder Buddy
Location: [TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK](TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK)

An AI-powered web application that generates professional test strategy documents from Jira tickets. React + Vite frontend, FastAPI backend, LLM integration.

## Repository Structure

- [API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW](API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW) — AI-assisted API contract validation UI
- [RESTASSURED_PROJECT_USING_AI](RESTASSURED_PROJECT_USING_AI) — REST Assured test automation framework
- [RAGs/BASIC RAG](RAGs/BASIC%20RAG) — Basic RAG implementation (local ChromaDB + Sentence Transformers)
- [RAGs/LANGFLOW_NAIVE_RAG_WITH_RAG_EXPLORER_UI](RAGs/LANGFLOW_NAIVE_RAG_WITH_RAG_EXPLORER_UI) — Langflow-powered RAG Explorer (Vercel-deployable)
- [RAGs/ADVANCE_RAG](RAGs/ADVANCE_RAG) — Advanced RAG system with hybrid search and reranking
- [TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK](TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK) — AI-driven test strategy generation tool

## How to Use This Workspace

1. Open the project folder that matches your learning goal.
2. Follow the project-specific README inside that folder.
3. Install dependencies and run the application or test suite as instructed.

## Goals of This Training

- Learn AI-assisted test automation concepts
- Build practical examples using modern tools
- Explore frontend, backend, and API testing patterns
- Combine traditional testing with LLM-based workflows
