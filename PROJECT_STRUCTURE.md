# RAG Agent Project Structure

This document provides a complete overview of the project structure and file organization.

## 📁 Project Overview

```
rag-agent/
├── README.md                    # Main project documentation
├── CONCEPTS.md                  # RAG concepts and technical implementation
├── PROJECT_STRUCTURE.md         # This file - project structure overview
├── quick-start.sh               # Automated setup script
├── server/                      # Backend API server
│   ├── app/                     # Python application package
│   │   ├── __init__.py          # Package initialization
│   │   ├── main.py              # FastAPI application and endpoints
│   │   ├── rag.py               # RAG pipeline implementation
│   │   ├── ingest.py            # Document processing and ingestion
│   │   └── settings_store.py    # Configuration management
│   ├── data/                    # Documents to be ingested (user-created)
│   ├── chroma_db/               # Vector database (auto-created)
│   ├── uploads/                 # Uploaded images and files
│   ├── widget/                  # Frontend files served by FastAPI
│   │   ├── chat.html            # Main chat interface
│   │   ├── test.html            # Testing page
│   │   └── settings-tester.html # Settings configuration page
│   ├── requirements.txt          # Python dependencies
│   ├── env.example              # Environment configuration template
│   └── README.md                # Server setup and usage guide
└── widget/                      # Frontend files (alternative location)
    ├── chat.html                # Chat interface
    ├── test.html                # Testing page
    └── embed.js                 # Embed script
```

## 🔧 File Descriptions

### Root Level Files

| File                   | Purpose       | Description                                                                         |
| ---------------------- | ------------- | ----------------------------------------------------------------------------------- |
| `README.md`            | Documentation | Comprehensive project guide with architecture, tech stack, and implementation steps |
| `CONCEPTS.md`          | Technical     | Detailed RAG concepts, implementation details, and architectural decisions         |
| `PROJECT_STRUCTURE.md` | Reference     | This file - detailed project structure and file organization                        |
| `quick-start.sh`       | Automation    | Bash script to automate initial setup and dependency installation                   |

### Server Backend (`server/`)

| File                    | Purpose             | Description                                                           |
| ----------------------- | ------------------- | --------------------------------------------------------------------- |
| `app/main.py`           | Core API            | FastAPI application with all endpoints (chat, settings, ingest, etc.) |
| `app/rag.py`            | RAG Pipeline        | Document retrieval, embeddings, and reranking implementation          |
| `app/ingest.py`         | Document Processing | File loading, chunking, and vector store ingestion                    |
| `app/settings_store.py` | Configuration       | Chatbot settings management with validation and persistence           |
| `app/__init__.py`       | Package             | Python package initialization                                         |
| `requirements.txt`      | Dependencies        | Python package requirements with specific versions                    |
| `env.example`           | Configuration       | Environment variables template for API keys and settings              |
| `README.md`             | Server Guide        | Detailed server setup, deployment, and troubleshooting                |

### Frontend Widget Files

#### **Primary Location (`server/widget/`)**
| File                    | Purpose           | Description                                                           |
| ----------------------- | ----------------- | --------------------------------------------------------------------- |
| `chat.html`             | Main Interface    | Complete chat interface with styling and functionality                |
| `test.html`             | Testing           | Testing page for debugging and development                            |
| `settings-tester.html`  | Configuration     | Settings management interface with live preview                       |

#### **Alternative Location (`widget/`)**
| File        | Purpose     | Description                                                 |
| ----------- | ----------- | ----------------------------------------------------------- |
| `chat.html` | Interface   | Main chat interface (same as server/widget/chat.html)       |
| `test.html` | Testing     | Testing page (same as server/widget/test.html)              |
| `embed.js`  | Integration | JavaScript embed script for external websites               |

## 🚀 Getting Started

### 1. Quick Setup

```bash
# Run the automated setup script
./quick-start.sh
```

### 2. Manual Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your API keys
# Start server
uvicorn app.main:app --reload --port 8000
```

## 🔍 Key Components

### Backend Architecture

- **FastAPI**: High-performance web framework with automatic API documentation
- **RAG Pipeline**: Document retrieval → embedding → reranking → generation
- **Chroma DB**: Local vector database for document storage
- **BGE Embeddings**: High-quality text embeddings with local deployment
- **Settings Management**: Dynamic configuration without server restarts
- **File Upload**: Image upload support for custom chat icons

### Frontend Architecture

- **Vanilla JavaScript**: Lightweight, no build process, easy to embed
- **Responsive Design**: Mobile-friendly chat interface
- **Dynamic Configuration**: UI updates based on server settings
- **Framer Integration**: Simple script tag integration
- **Live Preview**: Real-time settings updates in configuration interface

## 📚 API Endpoints

| Endpoint            | Method   | Purpose                                 |
| ------------------- | -------- | --------------------------------------- |
| `/`                 | GET      | API information and available endpoints |
| `/health`           | GET      | Health check and status                 |
| `/chat`             | POST     | Main chat endpoint with RAG processing  |
| `/settings`         | GET/POST | Chatbot configuration management        |
| `/suggested`        | GET      | Quick question suggestions              |
| `/ingest`           | POST     | Document ingestion into vector store    |
| `/ingest/stats`     | GET      | Ingestion statistics                    |
| `/collection/info`  | GET      | Vector store information                |
| `/collection/clear` | POST     | Clear all documents                     |
| `/upload/image`     | POST     | Upload custom chat icon images          |
| `/uploads/{filename}`| GET      | Serve uploaded images                   |

## 🛠️ Technology Stack

### Backend

- **Python 3.8+**: Core programming language
- **FastAPI**: Web framework and API
- **LangChain**: RAG pipeline orchestration
- **Chroma DB**: Vector database
- **BGE Models**: Embeddings and reranking
- **Uvicorn**: ASGI server
- **PyPDF2**: PDF document processing
- **python-docx**: DOCX document processing

### Frontend

- **HTML5**: Structure
- **CSS3**: Styling with CSS variables and modern features
- **Vanilla JavaScript**: Functionality
- **Responsive Design**: Mobile-first approach
- **Google Fonts**: Montserrat typography

### LLM Options

- **OpenAI GPT Models**: Production-ready, high quality
- **Ollama + Local Models**: Free alternative, privacy-focused

## 🔒 Security Features

- **CORS Configuration**: Configurable origin restrictions
- **Input Validation**: Pydantic models for request validation
- **Environment Variables**: Secure API key management
- **File Upload Validation**: Type and size restrictions
- **Rate Limiting**: Configurable request limits (optional)

## 📊 Performance Features

- **Async Processing**: Non-blocking API endpoints
- **Vector Caching**: Efficient document retrieval
- **Chunking Strategy**: Optimized document processing
- **Reranking**: Improved result relevance
- **Batch Processing**: Efficient embedding generation

## 🚀 Deployment Options

### Simple Hosting (MVP)

- **Render**: Easy deployment with automatic scaling
- **Railway**: Simple GitHub integration
- **Fly.io**: Global edge deployment

### Production Scale

- **AWS/GCP**: Full cloud infrastructure
- **Docker**: Containerized deployment
- **Load Balancing**: Multiple API instances

## 🔄 Development Workflow

1. **Setup**: Run `quick-start.sh` or follow manual setup
2. **Configuration**: Edit `.env` file with API keys
3. **Documents**: Place files in `server/data/`
4. **Ingestion**: Process documents into vector store
5. **Testing**: Test API endpoints locally
6. **Customization**: Use settings tester to configure chatbot
7. **Integration**: Add embed script to Framer website
8. **Deployment**: Deploy to chosen hosting platform

## 📝 File Modification Guide

### Adding New Features

- **New API Endpoints**: Add to `app/main.py`
- **RAG Improvements**: Modify `app/rag.py`
- **Document Types**: Extend `app/ingest.py`
- **UI Changes**: Update `server/widget/chat.html`
- **Settings**: Modify `app/settings_store.py`

### Configuration Changes

- **Environment Variables**: Add to `env.example` and `.env`
- **Default Settings**: Modify `app/settings_store.py`
- **Dependencies**: Update `requirements.txt`
- **CORS**: Update `ALLOWED_ORIGINS` in environment

## 🧪 Testing & Development

### Built-in Testing Tools

- **Health Check**: `/health` endpoint for monitoring
- **Test Page**: `http://localhost:8000/widget/test.html`
- **Settings Tester**: `http://localhost:8000/widget/settings-tester.html`
- **API Documentation**: Available at `/docs` when server is running

### Testing Commands

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

## 🎨 UI Customization

### Theme System

- **Accent Color**: Primary brand color for buttons and highlights
- **Secondary Color**: Borders and subtle elements
- **Background Color**: Chat widget background
- **Text Color**: Main text color
- **Live Preview**: See changes immediately in settings tester

### Branding Elements

- **Chat Title**: Main heading in chat widget
- **Chat Subtitle**: Descriptive text below title
- **Chat Icon**: Custom emoji or uploaded image
- **Suggested Questions**: Interactive question chips

### Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Flexible Layout**: Adapts to different screen sizes
- **Touch-Friendly**: Optimized for touch interactions
- **Cross-Browser**: Works on all modern browsers

## 🔄 Maintenance & Updates

### Regular Tasks

- **Document Updates**: Re-ingest when content changes
- **Model Updates**: Upgrade embedding models quarterly
- **Performance Monitoring**: Track response times and accuracy
- **Security Updates**: Keep dependencies updated

### Scaling Considerations

- **Vector DB Migration**: Chroma → Qdrant when outgrowing local storage
- **Load Balancing**: Multiple API instances for high traffic
- **CDN Integration**: Cache widget files globally
- **Database Optimization**: Index optimization and query tuning

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **API Key Issues**: Check `.env` file configuration
3. **Document Processing**: Verify file formats and permissions
4. **CORS Errors**: Update `ALLOWED_ORIGINS` in environment
5. **Chat Icon Issues**: Check image upload permissions and formats

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start with debug output
uvicorn app.main:app --reload --port 8000 --log-level debug
```

### Performance Issues

- **Slow Response Times**: Check embedding model performance
- **High Memory Usage**: Optimize chunking strategy
- **Large File Processing**: Use batch processing for large documents

## 📚 Additional Resources

- **Main README**: Complete project documentation
- **Server README**: Backend setup and deployment
- **CONCEPTS.md**: Technical implementation details
- **API Documentation**: Available at `/docs` when server is running
- **Code Comments**: Inline documentation in all source files

## 🎯 Project Status

### ✅ **Completed Features**

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

### 🚧 **Future Enhancements**

- **Multi-language Support**: Internationalization
- **User Authentication**: Login and user management
- **Chat History**: Persistent conversation storage
- **Analytics Dashboard**: Usage statistics and insights
- **Advanced Search**: Filters and search options
- **API Rate Limiting**: Production-ready security

---

This project structure provides a clean separation of concerns between backend API functionality and frontend widget integration, making it easy to develop, test, and deploy independently. The modular architecture allows for easy customization and scaling as your needs grow.
