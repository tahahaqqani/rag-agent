# RAG Agent Chatbot

## 🎯 Project Overview

This project creates a custom RAG (Retrieval-Augmented Generation) chatbot The chatbot is fully customizable, allowing you to update the interface, documents, suggested questions, branding, and more through a simple API. 

### 🎨 **Complete UI System**
- **Modern, sleek chat interface** with glassmorphism design
- **Responsive design** that works on all devices
- **Dynamic theming** with live color updates
- **Custom chat icons** (emoji or uploaded images)
- **Smooth animations** and transitions
- **Professional typography** using Montserrat font

### 🔧 **Full RAG Pipeline**
- **Document ingestion** for PDF, DOCX, TXT, and MD files
- **Vector embeddings** using BGE-small model
- **Chroma DB** for fast similarity search
- **Reranking** with BGE-reranker for better results
- **Intelligent chunking** with overlap for context preservation

### 🎛️ **Dynamic Configuration System**
- **Live settings updates** without server restarts
- **Real-time UI changes** in Framer
- **Comprehensive theming** (colors, fonts, spacing)
- **Custom branding** (title, subtitle, logo, icon)
- **Suggested questions** management
- **Chat parameters** (temperature, max tokens, context length)

### 🚀 **Multiple Integration Options**
- **Direct HTML embed** for Framer Custom Code
- **Iframe embed** for Framer Embed element
- **Script-based embed** (like Chatbase)
- **Local testing** with comprehensive test pages

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Framer Site   │    │   Widget Files   │    │  FastAPI Server │
│                 │    │                  │    │                 │
│  Custom Code    │───▶│   chat.html      │───▶│  /chat endpoint │
│  or Embed       │    │   test.html      │    │  /settings      │
│                 │    │   settings-tester│    │  /ingest        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                │                       ▼
                                │              ┌─────────────────┐
                                │              │   Vector Store  │
                                │              │   (Chroma DB)   │
                                │              │                 │
                                │              │  Document Index │
                                └──────────────┼  Embeddings     │
                                               │  Reranking      │
                                               └─────────────────┘
```

## 🚀 Quick Start (5 minutes)

### 1. **Start Your Server**
```bash
cd server
uvicorn app.main:app --reload --port 8000
```

### 2. **Add to Framer**
- **Option A**: Copy code from `widget/chat.html` into Framer Custom Code
- **Option B**: Use Framer Embed element with URL: `http://localhost:8000/widget/chat.html`

### 3. **Customize Your Chatbot**
- Open: `http://localhost:8000/widget/settings-tester.html`
- Change colors, title, icon, questions
- See live updates in your Framer page!

## 🎨 UI Features & Customization

### **Theme System**
- **Accent Color**: Primary brand color for buttons and highlights
- **Secondary Color**: Borders and subtle elements
- **Background Color**: Chat widget background
- **Text Color**: Main text color
- **Live Preview**: See changes immediately in settings tester

### **Branding Elements**
- **Chat Title**: Main heading in chat widget
- **Chat Subtitle**: Descriptive text below title
- **Chat Icon**: Custom emoji or uploaded image
- **Footer Text**: Optional footer message

### **Interactive Elements**
- **Suggested Questions**: Clickable question chips
- **Smooth Animations**: Fade-in effects and hover states
- **Responsive Design**: Works on mobile and desktop
- **Auto-resizing Input**: Textarea that grows with content

### **Chat Experience**
- **Typing Indicators**: Animated dots while processing
- **Message Bubbles**: User and assistant message styling
- **Bullet Point Formatting**: Clean, readable responses
- **Context-Aware**: Remembers conversation flow

## 🛠️ Tech Stack & Justification

### **Backend Technologies**

#### **FastAPI** - Web Framework
- **Why**: High performance, automatic API documentation, async support
- **Use Case**: REST API endpoints, real-time chat processing
- **Performance**: 10x faster than Flask, automatic OpenAPI docs

#### **Chroma DB** - Vector Database
- **Why**: Lightweight, local-first, easy to set up
- **Use Case**: Store document embeddings for similarity search
- **Features**: Persistent storage, metadata filtering, similarity search

#### **BGE Embeddings** - Text Embeddings
- **Why**: High quality, multilingual support, local deployment
- **Use Case**: Convert text chunks to vectors for similarity search
- **Model**: BGE-small-en-v1.5 (768 dimensions, fast inference)

#### **BGE Reranker** - Cross-Encoder
- **Why**: Improves retrieval quality by reranking results
- **Use Case**: Sort retrieved documents by relevance to query
- **Performance**: Significantly improves answer quality

### **Frontend Technologies**

#### **Vanilla JavaScript** - No Framework
- **Why**: Lightweight, no build process, easy to embed
- **Use Case**: Chat widget, API communication, dynamic updates
- **Bundle Size**: ~15KB vs 100KB+ for React

#### **Modern CSS** - Styling
- **Why**: CSS variables, flexbox, grid, animations
- **Use Case**: Responsive design, theming, smooth transitions
- **Features**: CSS custom properties, modern layout techniques

### **LLM Options**

#### **OpenAI GPT Models** (Recommended for Production)
- **Why**: High quality, reliable, well-documented
- **Use Case**: Generate chat responses
- **Cost**: ~$0.01-0.10 per 1K tokens
- **Models**: GPT-4o-mini, GPT-3.5-turbo

#### **Ollama + Local Models** (Free Alternative)
- **Why**: No API costs, privacy-focused
- **Use Case**: Development and testing
- **Models**: Llama 3, Mistral, CodeLlama
- **Performance**: Good quality with proper prompting

## 🔧 Setup Instructions

### 1. **Backend Setup**

```bash
# Clone and setup
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"
export MODEL_PROVIDER="openai"  # or "ollama"

# Start server
uvicorn app.main:app --reload --port 8000
```

### 2. **Document Ingestion**

```bash
# Place documents in server/data/
# Supported formats: PDF, DOCX, TXT, MD

# Run ingestion
python -c "from app.ingest import ingest_folder; print(ingest_folder('./data'))"
```

### 3. **Configuration**

```bash
# Update chatbot settings
curl -X POST http://localhost:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Your Company Assistant",
    "subtitle": "Ask me anything about our services",
    "accent": "#007bff",
    "suggested": [
      "What services do you offer?",
      "How much do you charge?",
      "Can you show me examples?",
      "How do I get started?"
    ]
  }'
```

## 🔍 Key Concepts Explained

### **RAG (Retrieval-Augmented Generation)**

1. **Document Processing**: Break documents into chunks (~600 tokens with 80 token overlap)
2. **Embedding**: Convert text chunks to numerical vectors using BGE model
3. **Indexing**: Store vectors in Chroma DB for fast similarity search
4. **Retrieval**: Find most similar document chunks to user query
5. **Reranking**: Use cross-encoder to improve result relevance
6. **Generation**: Create response using retrieved context + LLM

### **Vector Similarity Search**
- **Cosine Similarity**: Measures angle between vectors (0° = identical, 90° = unrelated)
- **L2 Normalization**: Ensures fair comparison between vectors of different lengths
- **K-Nearest Neighbors**: Retrieves top-K most similar documents

### **Context Window Management**
- **Chunking Strategy**: Balance between context completeness and retrieval precision
- **Overlap**: Maintains context continuity between chunks
- **Token Limits**: Respects LLM context window constraints

## 🔒 Security Considerations

### **CORS Configuration**
```python
ALLOWED_ORIGINS = [
    "https://your-framer-site.framer.website",
    "https://yourdomain.com"
]
```

### **Input Validation**
- Sanitize user inputs
- Rate limiting on chat endpoints
- File upload restrictions

### **API Security**
- Environment variable management
- Optional authentication for settings endpoint
- HTTPS enforcement in production

## 📊 Performance Optimization

### **Embedding Optimization**
- **Model Selection**: BGE-small for speed, BGE-large for quality
- **Batch Processing**: Process multiple documents simultaneously
- **Caching**: Cache embeddings for repeated queries

### **Retrieval Optimization**
- **Hybrid Search**: Combine dense (embeddings) + sparse (BM25) retrieval
- **Query Expansion**: Generate multiple query variations
- **Result Caching**: Cache common query results

### **Response Generation**
- **Streaming**: Real-time response generation
- **Context Pruning**: Remove irrelevant context to save tokens
- **Response Templates**: Pre-defined response patterns

## 🧪 Testing & Quality Assurance

### **Built-in Testing Tools**
- **Health Check**: `/health` endpoint for monitoring
- **Test Page**: `http://localhost:8000/widget/test.html`
- **Settings Tester**: `http://localhost:8000/widget/settings-tester.html`
- **API Documentation**: Available at `/docs` when server is running

### **Testing Commands**
```bash
# Test server health
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'

# View current settings
curl http://localhost:8000/settings

# Check collection info
curl http://localhost:8000/collection/info
```

## 🔄 Maintenance & Updates

### **Regular Tasks**
- **Document Updates**: Re-ingest when content changes
- **Model Updates**: Upgrade embedding models quarterly
- **Performance Monitoring**: Track response times and accuracy

### **Scaling Considerations**
- **Vector DB Migration**: Chroma → Qdrant when outgrowing local storage
- **Load Balancing**: Multiple API instances for high traffic
- **CDN Integration**: Cache widget files globally

## 💡 Current Features & Capabilities

### **✅ Implemented Features**
- **Full RAG Pipeline**: Document ingestion, embedding, retrieval, generation
- **Dynamic UI**: Live color updates, theme changes, branding
- **Custom Chat Icons**: Upload images or use emojis
- **Responsive Design**: Mobile-first, works on all devices
- **Settings Management**: Real-time configuration updates
- **Multiple File Types**: PDF, DOCX, TXT, MD support
- **Image Upload**: Custom chat icon management
- **Suggested Questions**: Interactive question chips
- **Smooth Animations**: Professional user experience
- **Error Handling**: Graceful fallbacks and user feedback

### **🚧 Future Enhancements**
- **Multi-language Support**: Internationalization
- **User Authentication**: Login and user management
- **Chat History**: Persistent conversation storage
- **Analytics Dashboard**: Usage statistics and insights
- **Advanced Search**: Filters and search options
- **API Rate Limiting**: Production-ready security

## 🆘 Troubleshooting

### **Common Issues**

#### **Chat Not Responding**
- Check API server status: `curl http://localhost:8000/health`
- Verify CORS configuration
- Check environment variables

#### **Poor Response Quality**
- Review document chunking strategy
- Adjust retrieval parameters
- Validate document quality

#### **Slow Performance**
- Optimize embedding model size
- Implement caching
- Scale infrastructure

### **Debug Commands**
```bash
# Check server health
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'

# View current settings
curl http://localhost:8000/settings

# Check collection info
curl http://localhost:8000/collection/info
```
