# Agent LLM RAG Chatbot

This application is a Retrieval-Augmented Generation (RAG) chatbot designed to answer questions about agricultural products, specifically formulated pesticides and agrochemicals registered in Brazil. It leverages data from the Embrapa Agrofit API to provide accurate, context-aware responses based on official product information such as usage indications, active ingredients, and documentation links.

Built with FastAPI for the backend, it integrates vector search, lexical retrieval, and reranking to deliver reliable answers. The system is containerized with Docker and uses PostgreSQL with pgvector for efficient document storage and querying.

---

# Key Features

### Intelligent Question Answering
Ask questions such as:


The chatbot returns answers grounded in official data and may include links to product labels (bulas) for verification.

### Hybrid Retrieval
The system combines:

- Keyword-based lexical search
- Semantic vector search

Results are then reranked to prioritize the most relevant documents before generating a response.

### Data Indexing
Product data is automatically fetched from the Embrapa Agrofit API, processed, chunked, embedded, and stored in a vector database for fast retrieval.

### API Endpoints
A simple REST API allows interaction with the chatbot and includes health check endpoints.

### Scalable and Production Ready
The application is containerized with Docker and includes a CI/CD pipeline using GitHub Actions. Automated tests ensure system reliability before deployment.

---

# How It Works

## 1. Data Ingestion

The system retrieves agricultural product data from the Embrapa Agrofit API.

Each product is validated using Pydantic models and converted into structured documents containing:

- Active ingredients
- Usage indications
- Target pests
- Application instructions
- Official documentation links

---

## 2. Indexing

Documents are processed and prepared for retrieval:

1. Text is split into smaller chunks.
2. Each chunk is embedded using a language model.
3. Embeddings are stored in PostgreSQL using the pgvector extension.

This enables efficient semantic search across large volumes of agricultural data.

---

## 3. Query Processing

When a user sends a question, the RAG pipeline performs multiple retrieval steps:

### Lexical Search
Uses PostgreSQL full-text search to match keywords and exact terms.

### Vector Search
Uses embeddings to find semantically similar documents using Maximal Marginal Relevance (MMR).

### Reranking
A reranker model evaluates retrieved documents and prioritizes the most relevant context.

### Response Generation
The final context is injected into a language model, which generates a natural language answer grounded in retrieved information.

---

## 4. Response

The chatbot returns a structured answer that may include:

- A clear explanation
- Product details
- Direct links to official product documentation

This ensures answers remain trustworthy and verifiable.

---

# Installation and Setup

## Prerequisites

- Python 3.12 or later
- Docker and Docker Compose
- Embrapa Agrofit API key
- API key for a language model provider (OpenRouter, Google GenAI, etc.)

---

# Local Development

## 1. Clone the Repository

```bash
git clone <repository-url>
cd agent-llm-rag
```

## 2. Set Up Environment Variables

- Copy `.env.example` to `.env` and fill in your keys:
  ```
  EMBRAPA_API_KEY=your-embrapa-key
  OPENROUTER_API_KEY=your-openrouter-key
  POSTGRES_USER=your-db-user
  POSTGRES_PASSWORD=your-db-password
  POSTGRES_DB=your-db-name
  POSTGRES_HOST=localhost
  POSTGRES_PORT=5432
  TABLE_NAME=vectorstore
  ```

## 3. Install Dependencies

- Using uv (recommended for speed):
  ```bash
  uv sync
  ```
- Or with pip:
  ```bash
  pip install -r requirements.txt
  ```

## 4. Start the Database

- Use Docker Compose to run PostgreSQL with pgvector:
  ```bash
  docker-compose up -d postgres
  ```

## 5. Index the Data

- Run the indexing script to populate the vector store with product data:
  ```bash
  uv run python -m chatapp.services.index
  ```
  This may take time depending on the number of pages fetched from the API.

## 6. Run the Application

```bash
uv run uvicorn chatapp.main:app --reload
```
The API will be available at `http://localhost:8000`.

## 7. Test It Out

- Health check: `GET /health`
- Chat: `POST /main` with JSON body `{"message": "Your question here"}`

---

# Production Deployment

- The app is configured for deployment via GitHub Actions (see `.github/workflows/deploy.yaml`).
- Set up secrets in your GitHub repo for API keys and server credentials.
- On push to `main`, tests run automatically, and if they pass, the app deploys to your server.
- Ensure your server has Docker and runs the compose file for the full stack.

---

# Usage Examples

### API Interaction

- **Health Check**:
  ```bash
  curl http://localhost:8000/health
  # Response: {"status": "ok"}
  ```

- **Chat Query**:
  ```bash
  curl -X POST http://localhost:8000/main \
    -H "Content-Type: application/json" \
    -d '{"message": "What pesticides are effective against soybean rust?"}'
  # Response: A JSON object with the answer and context.
  ```

### Running Tests

- Execute unit tests to verify functionality:
  ```bash
  uv run pytest tests/ -v
  ```
  Tests cover pipeline components, API calls, and data processing.

---

# Architecture Overview

- **Backend**: FastAPI handles requests, with CORS enabled for frontend integration.
- **Data Layer**: PostgreSQL with pgvector for vector storage; SQLAlchemy for async queries.
- **Retrieval Components**:
  - `LexicalRetriever`: Keyword search using PostgreSQL full-text search.
  - `VectorRetriever`: Semantic search with MMR for diversity.
  - `Reranker`: Refines results using a model like MiniLM.
- **LLM Integration**: Supports models from OpenAI, Google GenAI, or Ollama for answer generation.
- **Infrastructure**: Dockerized for easy deployment; GitHub Actions for CI/CD.

---

# Contributing

We welcome contributions! If you'd like to improve the chatbot, add features, or fix bugs:
1. Fork the repo and create a feature branch.
2. Write tests for new functionality.
3. Ensure all tests pass before submitting a pull request.
4. Follow the existing code style (use Ruff for linting).

For questions or ideas, open an issue on GitHub.

---

# License

This project is licensed under the MIT License. See `LICENSE` for details.

---

This chatbot aims to make agricultural information more accessible, helping farmers and professionals make informed decisions based on reliable data. If you have feedback or need help getting started, feel free to reach out!

---

# Local Development

## 1. Clone the Repository

```bash
git clone <repository-url>
cd agent-llm-rag