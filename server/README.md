# Server Setup Guide

Quick setup guide for the RAG chatbot server backend.

## Quick Start

### 1. Prerequisites

- Python 3.8+ installed
- pip package manager
- Git (for cloning the repository)

### 2. Installation

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the server directory:

```bash
# LLM Configuration
MODEL_PROVIDER=openai  # or "ollama"
OPENAI_API_KEY=your-openai-api-key-here
GEN_MODEL=gpt-4o-mini  # or "llama3" for Ollama

# Ollama Configuration (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434

# Vector Store Configuration
CHROMA_DIR=./chroma_db
COLLECTION=docs
EMBED_MODEL=BAAI/bge-small-en-v1.5
RERANK_MODEL=BAAI/bge-reranker-base

# API Configuration
ALLOWED_ORIGINS=https://your-framer-site.framer.website,https://yourdomain.com

# Chunking Configuration
CHUNK_SIZE=600
CHUNK_OVERLAP=80
TOKENIZER_MODEL=gpt-4o-mini

# File Upload Configuration
MAX_FILE_SIZE=5242880  # 5MB in bytes
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/gif,image/webp
```

### 4. Start the Server

```bash
# Start with auto-reload (development)
uvicorn app.main:app --reload --port 8000

# Start in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## 📚 Document Ingestion

### 1. Prepare Documents

Place your documents in the `server/data/` directory:

- **PDF files** (.pdf) - Will be processed page by page
- **DOCX files** (.docx) - Will extract structured text
- **Text files** (.txt) - Plain text documents
- **Markdown files** (.md, .markdown) - Markdown formatted documents

### 2. Ingest Documents

```bash
# Ingest all documents in the data directory
python -c "from app.ingest import ingest_folder; print(ingest_folder('./data'))"

# Ingest a specific file
python -c "from app.ingest import ingest_single_file; print(ingest_single_file('./data/example.pdf'))"

# Ingest with custom chunking parameters
python -c "from app.ingest import ingest_folder; print(ingest_folder('./data', chunk_size=800, overlap=100))"
```

### 3. Check Ingestion Status

```bash
# View vector store statistics
curl http://localhost:8000/ingest/stats

# View collection information
curl http://localhost:8000/collection/info
```

## ⚙️ Configuration Management

### 1. Update Chatbot Settings

```bash
# Update basic settings
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

# View current settings
curl http://localhost:8000/settings

# Reset to defaults
curl -X POST http://localhost:8000/settings/reset
```

### 2. Settings Schema

```json
{
  "title": "AI Assistant",
  "subtitle": "Ask me anything about our services and process.",
  "accent": "#026CBD",
  "suggested": [
    "What services do you offer?",
    "Can you show recent projects?",
    "How does pricing work?",
    "What is your typical timeline?"
  ],
  "theme": {
    "accent_color": "#026CBD",
    "secondary_color": "#6c757d",
    "background_color": "#ffffff",
    "text_color": "#333333"
  },
  "chat_settings": {
    "max_context_length": 3000,
    "temperature": 0.2,
    "max_tokens": 140,
    "enable_streaming": false
  },
  "chat_icon": "💬",
  "chat_icon_text": "Chat with us"
}
```

## 🖼️ Image Upload & Custom Icons

### 1. Upload Custom Chat Icon

```bash
# Upload an image file
curl -X POST http://localhost:8000/upload/image \
  -F "file=@/path/to/your/icon.png" \
  -F "type=chat_icon"

# Response will include the file URL
{
  "url": "/uploads/icon_123456.png",
  "filename": "icon_123456.png",
  "size": 24576,
  "type": "image/png"
}
```

### 2. Supported Image Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **GIF** (.gif)
- **WebP** (.webp)

### 3. Image Management

```bash
# View uploaded images
ls -la uploads/

# Remove old images
rm uploads/old_icon.png

# Update settings to use new icon
curl -X POST http://localhost:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "chatIcon": "/uploads/new_icon.png"
  }'
```

## 🔧 API Endpoints

### Core Endpoints

| Endpoint            | Method   | Description                             |
| ------------------- | -------- | --------------------------------------- |
| `/`                 | GET      | API information and available endpoints |
| `/health`           | GET      | Health check                            |
| `/chat`             | POST     | Main chat endpoint                      |
| `/settings`         | GET/POST | Chatbot configuration                   |
| `/suggested`        | GET      | Quick question suggestions              |
| `/ingest`           | POST     | Document ingestion                      |
| `/ingest/stats`     | GET      | Ingestion statistics                    |
| `/collection/info`  | GET      | Vector store information                |
| `/collection/clear` | POST     | Clear all documents                     |
| `/upload/image`     | POST     | Upload custom chat icon images          |
| `/uploads/{filename}`| GET      | Serve uploaded images                   |

### Chat Endpoint

```bash
# Send a chat message
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "What services do you offer?",
    "session_id": "user123"
  }'
```

Response:

```json
{
  "answer": "Based on our documentation, we offer the following services...",
  "context_used": 1,
  "response_time": 1.23
}
```

### Ingest Endpoint

```bash
# Ingest documents
curl -X POST http://localhost:8000/ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "input_path": "./data",
    "source_tag": "company_docs",
    "chunk_size": 600,
    "overlap": 80
  }'
```

## 🧪 Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "model_provider": "openai",
  "llm_model": "gpt-4o-mini"
}
```

### 2. Test Chat

```bash
# Simple test
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question": "Hello, how are you?"}'
```

### 3. Test Settings

```bash
# Get current settings
curl http://localhost:8000/settings

# Test suggested questions
curl http://localhost:8000/suggested
```

### 4. Test Image Upload

```bash
# Test with a sample image
curl -X POST http://localhost:8000/upload/image \
  -F "file=@/path/to/test_image.png" \
  -F "type=chat_icon"
```

## 🚀 Deployment

### Option 1: Render (Recommended for MVP)

1. **Create Render Account**: Sign up at [render.com](https://render.com)
2. **Connect Repository**: Link your GitHub repository
3. **Configure Service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add all variables from your `.env` file

### Option 2: Railway

1. **Create Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Deploy from GitHub**: Connect your repository
3. **Set Environment Variables**: Add all required environment variables
4. **Deploy**: Railway will automatically detect and deploy your FastAPI app

### Option 3: Fly.io

1. **Install Fly CLI**: `curl -L https://fly.io/install.sh | sh`
2. **Login**: `fly auth login`
3. **Create App**: `fly apps create your-rag-chatbot`
4. **Deploy**: `fly deploy`

### Option 4: Local Production

```bash
# Install production server
pip install gunicorn

# Create gunicorn config
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
EOF

# Start production server
gunicorn -c gunicorn.conf.py app.main:app
```

## 🔒 Security Considerations

### 1. CORS Configuration

Update `ALLOWED_ORIGINS` in your environment variables:

```bash
# For production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# For development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 2. API Key Security

- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider using a secrets management service in production

### 3. File Upload Security

- Validate file types and sizes
- Scan uploaded files for malware
- Store files outside web root when possible
- Use secure file naming (avoid user input in filenames)

### 4. Rate Limiting

For production use, consider adding rate limiting:

```bash
pip install slowapi
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Ensure you're in the correct directory
cd server

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Chroma DB Issues

```bash
# Clear vector store
curl -X POST http://localhost:8000/collection/clear

# Check collection info
curl http://localhost:8000/collection/info
```

#### 3. OpenAI API Errors

```bash
# Check API key
echo $OPENAI_API_KEY

# Test API connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### 4. Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama (if not running)
ollama serve
```

#### 5. File Upload Issues

```bash
# Check uploads directory permissions
ls -la uploads/

# Ensure directory exists
mkdir -p uploads

# Set proper permissions
chmod 755 uploads/
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start server with debug
uvicorn app.main:app --reload --port 8000 --log-level debug
```

### Logs

Check server logs for detailed error information:

```bash
# View real-time logs
tail -f server.log

# Search for errors
grep -i error server.log
```

## 📊 Monitoring

### 1. Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Custom health check script
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $response -eq 200 ]; then
    echo "Server is healthy"
    exit 0
else
    echo "Server is unhealthy (HTTP $response)"
    exit 1
fi
```

### 2. Performance Monitoring

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/health"

# Create curl-format.txt
cat > curl-format.txt << EOF
     time_namelookup:  %{time_namelookup}\\n
        time_connect:  %{time_connect}\\n
     time_appconnect:  %{time_appconnect}\\n
    time_pretransfer:  %{time_pretransfer}\\n
       time_redirect:  %{time_redirect}\\n
  time_starttransfer:  %{time_starttransfer}\\n
                     ----------\\n
          time_total:  %{time_total}\\n
EOF
```

### 3. RAG Pipeline Monitoring

```bash
# Check embedding model status
curl http://localhost:8000/health

# Monitor document ingestion
curl http://localhost:8000/ingest/stats

# Check vector store health
curl http://localhost:8000/collection/info
```

## 🔄 Updates and Maintenance

### 1. Update Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip audit
```

### 2. Backup Configuration

```bash
# Backup current config
cp config.json config.backup.$(date +%Y%m%d_%H%M%S).json

# Backup vector store
tar -czf chroma_backup_$(date +%Y%m%d_%H%M%S).tar.gz chroma_db/

# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/
```

### 3. Restart Server

```bash
# Graceful restart
pkill -f uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Model Updates

```bash
# Update embedding models
pip install --upgrade sentence-transformers

# Update reranker models
pip install --upgrade FlagEmbedding

# Restart server to use new models
pkill -f uvicorn
uvicorn app.main:app --reload --port 8000
```

## 🎨 UI Customization

### 1. Theme Configuration

```bash
# Update theme colors
curl -X POST http://localhost:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "theme": {
      "accent_color": "#667eea",
      "secondary_color": "#f8fafc",
      "background_color": "#ffffff",
      "text_color": "#475569"
    }
  }'
```

### 2. Branding Updates

```bash
# Update title and subtitle
curl -X POST http://localhost:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Your Company Name",
    "subtitle": "Your company tagline here"
  }'
```

### 3. Suggested Questions

```bash
# Update suggested questions
curl -X POST http://localhost:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "suggested": [
      "What services do you offer?",
      "How can I get started?",
      "What are your pricing plans?",
      "Can you help me with a specific issue?"
    ]
  }'
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Chroma DB Guide](https://docs.trychroma.com/)
- [BGE Embeddings](https://huggingface.co/BAAI/bge-small-en-v1.5)
- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [Main Project README](../README.md)
- [Technical Concepts](../CONCEPTS.md)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review server logs for error messages
3. Verify environment variables are set correctly
4. Ensure all dependencies are installed
5. Check if the required services (OpenAI/Ollama) are accessible

For additional help, check the main project README or create an issue in the repository.

## 🎯 Current Features

### ✅ **Implemented Features**

- **Full RAG Pipeline**: Document ingestion, embedding, retrieval, generation
- **Dynamic Settings**: Real-time configuration updates
- **Image Upload**: Custom chat icon management
- **Multiple File Types**: PDF, DOCX, TXT, MD support
- **Theme System**: Comprehensive color and styling customization
- **API Documentation**: Automatic OpenAPI/Swagger docs
- **Health Monitoring**: Built-in health checks and status endpoints
- **Error Handling**: Graceful fallbacks and user feedback

### 🚧 **Future Enhancements**

- **User Authentication**: Login and user management
- **Advanced Analytics**: Usage statistics and insights
- **Multi-tenant Support**: Separate data for different organizations
- **API Rate Limiting**: Production-ready security
- **Streaming Responses**: Real-time response generation
- **Advanced Search**: Filters and search options

---

This server provides a robust, scalable backend for your RAG chatbot with comprehensive configuration options, security features, and monitoring capabilities.
