# AI Tester Training
This workspace contains a collection of AI-assisted testing projects designed for hands-on learning, automation practice, and experimentation with modern test engineering tools.

## Projects Included

### 1. API Contract Validator with Langflow UI
Location: [API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW](API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW)

A React + Vite application that validates API contracts using JSON schemas and an AI-powered Langflow backend. It helps users test whether an API response matches the expected structure and format.

Highlights:
- Paste a curl command or API URL
- Provide a JSON schema for validation
- Send the request to Langflow for AI-assisted contract validation
- View structured results in the UI

### 2. REST Assured API Testing Framework
Location: [RESTASSURED_PROJECT_USING_AI](RESTASSURED_PROJECT_USING_AI)

A Java-based API automation framework built with REST Assured, TestNG, and supporting libraries. It demonstrates a structured approach to API testing with reusable services, POJOs, configuration management, and detailed reporting.

Highlights:
- Authentication and booking API coverage
- Service-layer test design
- POJO-based request/response modeling
- Logging, assertions, and test reporting

### 3. Advanced RAG Explorer (New!)
Location: [RAGs/ADVANCE_RAG](RAGs/ADVANCE_RAG)

An **end-to-end Advanced Retrieval-Augmented Generation (RAG)** application that ingests 5,000 VWO test cases, indexes them with hybrid (dense + sparse) vectors in Qdrant, and answers questions using a multi-stage pipeline with LLM generation. Built as a teaching demo for The Testing Academy.

**Pipeline:** Query Rewriting → Hybrid Embedding (bge-m3) → Hybrid Search (Qdrant + RRF fusion) → Cross-Encoder Reranking → LLM Generation (DeepSeek Chat)

Highlights:
- 5-stage RAG pipeline with live UI tracking
- Hybrid retrieval (dense + sparse vectors) for better search accuracy
- Qdrant vector DB in embedded mode (no Docker needed)
- Query auto-detection: answer mode vs generate mode
- Interactive frontend with 4 tabs (Upload, Ingest, Chunks, Chat)
- Standalone HTML explainer page with animated architecture diagrams

### 4. Test Strategy Builder Buddy
Location: [TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK](TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK)

An AI-powered web application that generates professional test strategy documents from Jira tickets. It combines frontend, backend, and LLM integration to streamline strategy creation.

Highlights:
- Jira input support
- AI-generated strategy output
 - React + Vite frontend
- FastAPI backend and LLM integration

## Repository Structure

- [API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW](API_CONTRACT_VALIDATOR_FRONTEND_CALLING_LANGFLOW) – AI-assisted API contract validation UI
- [RESTASSURED_PROJECT_USING_AI](RESTASSURED_PROJECT_USING_AI) � REST Assured test automation framework
- [RAGs/ADVANCE_RAG](RAGs/ADVANCE_RAG) – Advanced RAG system for VWO test case retrieval and generation
- [RAGs/BASIC RAG](RAGs/BASIC%20RAG) � Basic RAG implementation
- [TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK](TEST_STRATEGY_BUILDER_BUDDY_USING_BLAST_FRAMEWORK) – AI-driven test strategy generation tool

## How to Use This Workspace

1. Open the project folder that matches your learning goal.
2. Follow the project-specific README inside that folder.
3. Install dependencies and run the application or test suite as instructed.

## Goals of This Training

- Learn AI-assisted test automation concepts
- Build practical examples using modern tools
- Explore frontend, backend, and API testing patterns
- Combine traditional testing with LLM-based workflows