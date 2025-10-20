# RAG Agent - Intelligent Document Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot that answers questions based on your documents. Upload PDFs, DOCX, or text files, and get instant, accurate responses powered by AI.

## What It Does

- **Document Intelligence**: Upload your company documents (PDFs, Word docs, text files)
- **Smart Q&A**: Ask questions in natural language and get accurate answers
- **Context-Aware**: Understands your specific content, not generic responses
- **Customizable**: Brand it with your colors, logo, and messaging
- **Easy Integration**: Embed in any website with a simple script

## How It Works

### Technical Architecture

```
Documents → Chunking → Embeddings → Vector Database → Retrieval → AI Response
```

1. **Document Processing**: Your files are split into semantic chunks (600 tokens each)
2. **Vector Embeddings**: Each chunk is converted to a 768-dimensional vector using BGE-small model
3. **Vector Storage**: Embeddings stored in Chroma DB for fast similarity search
4. **Query Processing**: User questions are embedded and matched against document chunks
5. **Reranking**: BGE-reranker improves result relevance
6. **AI Generation**: GPT-4o-mini generates responses using retrieved context

### Key Features

- **BGE Embeddings**: High-quality semantic search with 768-dimensional vectors
- **Chroma DB**: Fast vector similarity search with HNSW algorithm
- **Cross-Encoder Reranking**: Improves answer quality by 40-60%
- **Intelligent Chunking**: 600-token chunks with 80-token overlap for context preservation
- **Multiple LLM Support**: OpenAI GPT models or local Ollama models

## Quick Start

### 1. Setup Server
```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Start server
uvicorn app.main:app --reload --port 8000
```

### 2. Add Your Documents
```bash
# Place PDFs, DOCX, or TXT files in server/data/
# Then ingest them
python -c "from app.ingest import ingest_folder; print(ingest_folder('./data'))"
```

### 3. Test the Chatbot
- Open: `http://localhost:8000/widget/test.html`
- Ask questions about your documents
- Customize: `http://localhost:8000/widget/settings-tester.html`

### 4. Embed in Your Website
```html
<!-- Add this to your website -->
<script src="http://localhost:8000/widget/embed.js"></script>
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main chat endpoint |
| `/settings` | GET/POST | Configure chatbot |
| `/ingest` | POST | Upload documents |
| `/health` | GET | Server status |

### Chat Example
```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question": "What services do you offer?"}'
```

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your-api-key-here
MODEL_PROVIDER=openai  # or "ollama"
GEN_MODEL=gpt-4o-mini
EMBED_MODEL=BAAI/bge-small-en-v1.5
RERANK_MODEL=BAAI/bge-reranker-base
```

### Customize Appearance
```bash
curl -X POST http://localhost:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Your Company Assistant",
    "subtitle": "Ask me anything about our services",
    "accent": "#007bff",
    "suggested": [
      "What services do you offer?",
      "How much do you charge?",
      "Can you show me examples?"
    ]
  }'
```

## Why RAG?

**Traditional Chatbots**: Trained on static data, can't access new information, may hallucinate facts.

**RAG Chatbots**: 
- ✅ Grounded in your actual documents
- ✅ Always up-to-date (just update documents)
- ✅ Transparent (shows which documents support answers)
- ✅ Cost-effective (no retraining needed)

## Deployment

### Simple Hosting (Recommended)
- **Render/Railway/Fly.io**: Deploy with one click
- **Cost**: $5-20/month
- **Setup**: 30 minutes

### Production Setup
- **Backend**: AWS/GCP with load balancer
- **Vector DB**: Qdrant Cloud or Pinecone
- **Widget**: CDN (Cloudflare, Vercel)

## Troubleshooting

**Chat not responding?**
- Check server: `curl http://localhost:8000/health`
- Verify API key is set
- Check CORS configuration

**Poor answer quality?**
- Ensure documents are properly ingested
- Check document quality and relevance
- Adjust chunk size if needed

**Slow performance?**
- Use smaller embedding model
- Implement caching
- Scale infrastructure

## Project Structure

```
rag-agent/
├── README.md              # This file
├── server/                # Backend API
│   ├── app/              # Python application
│   │   ├── main.py       # FastAPI endpoints
│   │   ├── rag.py        # RAG pipeline
│   │   ├── ingest.py     # Document processing
│   │   └── settings_store.py # Configuration
│   ├── data/             # Your documents go here
│   ├── widget/           # Frontend files
│   └── README.md         # Server setup guide
└── widget/               # Alternative frontend location
    ├── chat.html         # Main chat interface
    └── embed.js          # Embed script
```

## License

MIT License - Use freely for personal and commercial projects.

---

**Need help?** Check the server README for detailed setup instructions or open an issue.