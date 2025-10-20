# KcartBot - Advanced AI Agri-Commerce Assistant

An end-to-end, production-minded assistant for Ethiopian agri-commerce. It supports multi-turn chat, English/Amharic/Amhar-glish, RAG over a product knowledge base, supplier pricing insights, AI image generation, MLOps demos, and full Dockerization. Built with FastAPI, Streamlit, PostgreSQL + Chroma, and an MCP-style tool layer.

## 🏗️ Architecture Overview

```mermaid
graph TB
    U[User] --> S[Streamlit Dashboard]
    U -->|HTTP| A[FastAPI]
    S --> A
    A --> L[LLM Chat Logic]
    L --> T[MCP Server & Tools]
    T --> R[(PostgreSQL)]
    T --> V[(ChromaDB)]
    T --> G[Image Generation]
    V --> Q[Embeddings]
    A --> I[Language Detection]
    A --> D[Analytics/Monitoring]

    subgraph External APIs
      G --> H1[Hugging Face]
      G --> H2[Replicate]
      G --> H3[Unsplash]
    end

    subgraph Datasets
      X1[1-yr Competitor Pricing] --> R
      X2[1-yr Transactions] --> R
      X3[Products + Knowledge] --> R & V
    end

    subgraph MLOps
      MR[Model Registry]
      DEP[Deployment]
      MON[Monitoring]
      HC[Health Checks]
    end

    T --> MR
    MR --> DEP
    A --> MON
    T --> MON
    A --> HC
```

## 🚀 Key Features

- **Customer flow**: Registration → RAG discovery → conversational ordering → COD auto-confirmation (5s simulation)
- **Supplier flow**: Conversational product onboarding → expiry tracking → pricing insights from competitor/history → optional image generation
- **RAG**: Chroma-powered retrieval over storage, nutrition, recipes, seasonal info
- **Multi-language**: English, Amharic (አማርኛ), Amhar-glish detection and responses
- **Image generation**: Hugging Face/Replicate/Unsplash with caching and fallbacks
- **MCP-style tools**: Structured operations for users, products, orders, pricing insights, and knowledge
- **MLOps demo**: Model registry, monitoring, health checks, deployments
- **Dockerized**: Single-command local bring-up; persistent volumes

## 📁 Project Structure

```
kcartbot/
├── data/
│   ├── __init__.py
│   ├── generate_data.py           # 1-year synthetic data generator
│   └── generated_images/
├── src/
│   ├── main.py                    # FastAPI API server
│   ├── config.py
│   ├── image_generation.py
│   ├── dashboard/
│   │   ├── analytics.py
│   │   ├── chat.py
│   │   ├── database.py
│   │   ├── knowledge.py
│   │   ├── orders.py
│   │   └── products.py
│   ├── database/connection.py     # Relational DB init/connection
│   ├── mcp/server.py              # MCP-like tool server
│   ├── mlops/
│   │   ├── deployment.py
│   │   ├── health_check.py
│   │   ├── model_registry.py
│   │   └── monitoring.py
│   ├── services/chat_service.py   # LLM chat orchestrator
│   ├── services/rag_service.py    # Chroma-backed RAG
│   └── utils/
│       ├── language_detection.py
│       └── helpers.py
├── demos/demo_image_generation.py
├── scripts/
│   ├── setup_environment.py
│   ├── setup_with_guides.py
│   └── verify_api_tokens.py
├── tests/
│   ├── test_basic.py
│   ├── test_chat.py
│   ├── test_dashboard.py
│   └── test_kcartbot.py
├── dashboard.py                   # Streamlit UI entry
├── launch_dashboard.py            # Helper launcher
├── inspect_sqlite_schema.py
├── windows_postgresql_setup.py
├── setup_postgresql_windows.ps1
├── setup_postgresql_windows.bat
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run_tests.py
├── pytest.ini
├── env.example
└── README.md
```

## 🧰 Tech Stack

- **Backend**: FastAPI, Pydantic, Uvicorn
- **LLM**: Google Generative AI (Gemini) via `google-generativeai`
- **MCP-style tools**: Custom tool server in `src/mcp/server.py`
- **Relational DB**: PostgreSQL (dev alt: SQLite)
- **Vector DB**: ChromaDB + sentence-transformers
- **UI**: Streamlit dashboard
- **Data**: Faker, Pandas, NumPy
- **MLOps**: Registry, monitoring, health checks (see `src/mlops`)
- **Container**: Docker + docker-compose

## 🗄️ Databases (Hybrid)

- **PostgreSQL**: Users, products, suppliers, orders, pricing history, transactions
- **ChromaDB**: Product knowledge (storage, nutrition, recipes, seasonal tips) for RAG

You can start with SQLite for quick local runs and switch to PostgreSQL for realistic evaluation.

## 🧪 Dataset Generation (1 Year)

Generate a full year of data: products (≥15), competitor pricing (daily/weekly), and transactions.

```bash
python data/generate_data.py
```

Outputs include realistic Ethiopian market data and optional AI-generated images in `data/generated_images/`.

## ⚙️ Setup

### 1) Clone and environment

```bash
git clone <your-fork-or-repo-url>
cd kcartbot
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Configure environment

Copy `env.example` to `.env` and fill in values:

```bash
GEMINI_API_KEY=your_gemini_api_key

# Relational DB (choose one)
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/kcartbot
# or for quickstart
# DATABASE_URL=sqlite:///./kcartbot.db

# Vector DB
VECTOR_DB_PATH=./chroma_db

# Image generation
HUGGINGFACE_TOKEN=your_token
REPLICATE_API_TOKEN=your_token
UNSPLASH_ACCESS_KEY=your_key

IMAGE_GENERATION_ENABLED=true
DEFAULT_IMAGE_API=huggingface
GENERATED_IMAGES_DIR=data/generated_images

DEBUG=True
HOST=0.0.0.0
PORT=8000
```

Verify tokens and environment quickly:

```bash
python scripts/verify_api_tokens.py
```

### 3) PostgreSQL setup (Windows friendly)

Use any of the following:

- `setup_postgresql_windows.ps1` or `setup_postgresql_windows.bat`
- `windows_postgresql_setup.py` for programmatic setup

After DB is up, ensure schema is created on API startup (the API runs `init_database()` on startup).

### 4) Vector DB (Chroma) init

Chroma data lives in `./chroma_db`. RAG will build/refresh collections on first use through `RAGService`.

### 5) Generate data and sample images

```bash
python data/generate_data.py
python demos/demo_image_generation.py
```

### 6) Run

- Streamlit dashboard

```bash
streamlit run dashboard.py
```

- API server

```bash
python src/main.py
```

- One-command helper

```bash
python launch_dashboard.py
```

## 🐳 Docker

Quick start:

```bash
copy env.example .env  # Windows
docker-compose up -d
```

Services:

- Dashboard: `http://localhost:8501`
- API: `http://localhost:8000/docs`

The compose file uses SQLite by default for convenience. To use PostgreSQL, set `DATABASE_URL` to your Postgres instance before `docker-compose up`.

Helpful commands:

```bash
docker build -t kcartbot:latest .
docker run -d -p 8501:8501 -p 8000:8000 -e GEMINI_API_KEY=xxx -v %cd%\data:/app/data -v %cd%\chroma_db:/app/chroma_db kcartbot:latest
docker logs -f kcartbot
```

## 💬 Usage Guide (End-to-End Scripts)

### Customer (English/Amharic/Amhar-glish)

```
User: I want to register as a customer
Bot: Welcome! Please provide your name and phone number.
User: My name is Alem, phone +251911234567
Bot: Great! Where is your default location?
User: Addis Ababa
Bot: Registration complete! How can I help you today?

User: How should I store tomatoes?
Bot: Store tomatoes at room temperature until ripe, then refrigerate... (RAG)

User: I want 5kg of red onions and 2 liters of milk.
Bot: Available at 69 ETB/kg and 45 ETB/liter. When is delivery?
User: Tomorrow
Bot: Payment is Cash on Delivery. Confirming order...
... 5 seconds pass ...
Bot: Order Confirmed for COD. Delivery tomorrow. Thank you!
```

Amharic and Amhar-glish examples are handled automatically by `language_detection`.

### Supplier

```
User: I want to add tomatoes
Bot: How many kg do you have?
User: 100
Bot: Delivery date(s)?
User: Friday
Bot: Expiry date (optional)?
User: Next Wednesday
Bot: For Tomatoes, current competitor prices are: Local ~50 ETB/kg, Supermarkets ~65 ETB/kg. Based on recent sales, 55 ETB moves stock quickly. What price do you want to set?
User: 56 ETB
Bot: Shall I generate a fresh image for these tomatoes?
User: Yes
Bot: Image generated and attached. Product added.

User: Check my stock
Bot: Tomatoes 100kg (expires in 6 days). Suggest 20% flash sale if under 2 days.

User: How many deliveries do I have for Tuesday?
Bot: You have 3 scheduled deliveries for Tuesday...
```

## 🔌 MCP-style Tools

The MCP server (`src/mcp/server.py`) exposes structured tools used by chat flows and API endpoints, including: `register_user`, `search_products`, `get_product_info`, `create_order`, `get_pricing_insights`, `get_supplier_orders`, plus knowledge queries routed via `RAGService`.

Discover tools via the API:

```bash
GET /tools
```

## 🧠 RAG

- Vector store: ChromaDB at `VECTOR_DB_PATH`
- Embeddings: `sentence-transformers`
- Indexed fields: product docs (storage, nutrition, recipes, seasonal)

Search endpoint examples:

```bash
GET /knowledge/search?query=How%20to%20store%20avocados
GET /knowledge/products/{product_id}
GET /knowledge/stats
```

## 🧪 Testing

```bash
pytest -q
python run_tests.py
```

## 🧑‍💻 MLOps Demo

```bash
python mlops_demo.py            # all components
python mlops_demo.py --component registry
python mlops_demo.py --component deployment
python mlops_demo.py --component monitoring
python mlops_demo.py --component health
```

## 🧭 Demo Checklist (for the 45-min exam)

- Architecture walkthrough (LLM ↔ MCP ↔ PostgreSQL/Chroma ↔ Image Gen)
- Generate 1-year data; show competitor and transaction samples
- Customer journey including COD 5s auto-confirmation
- Supplier onboarding with pricing insights and image generation
- RAG Q&A in English/Amharic/Amhar-glish
- Docker bring-up and persistence explanation
- MLOps registry/monitoring/health demo

## 📈 Future Improvements

- Kubernetes + cloud Postgres/managed vector DB
- WebSocket live updates and supplier notifications
- Voice interface (STT/TTS) and mobile UI
- Fine-tuned models and adaptive pricing strategies

## 📄 License

MIT (see LICENSE if included).

— Empowering Ethiopian agriculture through AI-driven commerce 🇪🇹
