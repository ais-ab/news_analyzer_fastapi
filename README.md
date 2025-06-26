# News Analyzer - React + FastAPI

A modern news analysis platform with AI-powered filtering and summarization, migrated from Streamlit to React frontend with FastAPI backend.

## 🚀 Features

- **AI-Powered News Analysis**: Intelligent filtering and summarization of news articles
- **Source Management**: Add and manage news sources from various categories
- **Business Interest Tracking**: Define and track your business interests
- **Real-time Analysis**: Get instant insights from multiple news sources
- **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Authentication**: Secure client-based authentication system
- **PostgreSQL Database**: Robust, scalable database for production use

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Database ORM with PostgreSQL
- **Pydantic**: Data validation and serialization
- **LangChain**: AI/LLM integration for news analysis
- **Scrapy**: Web scraping for news articles

### Frontend (React)
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **React Router**: Client-side routing
- **React Query**: Server state management
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons

### Database
- **PostgreSQL**: Primary database for production and development
- **SQLite**: Fallback option for development (legacy)

## 📁 Project Structure

```
news_analyzer3/
├── backend/                 # FastAPI backend
│   ├── api/
│   │   ├── routes/         # API endpoints
│   │   │   ├── auth.py     # Authentication routes
│   │   │   ├── sources.py  # Source management
│   │   │   ├── news.py     # News analysis
│   │   │   └── analysis.py # Business interests & stats
│   │   └── schemas.py      # Pydantic models
│   ├── database/
│   │   ├── database.py     # Database configuration
│   │   └── models.py       # SQLAlchemy models
│   ├── utils/              # Core utility functions
│   │   ├── llm_functions.py    # AI/LLM integration
│   │   ├── source_functions.py # Source management
│   │   ├── trafilatura_spider.py # Web scraping
│   │   ├── constants.py        # Configuration
│   │   └── ...                 # Other utilities
│   ├── db/                 # Database files
│   ├── tmp/                # Temporary files
│   ├── main.py             # FastAPI application
│   ├── migrate_to_postgres.py # Migration script
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── contexts/       # React contexts
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   ├── App.tsx         # Main app component
│   │   └── index.tsx       # Entry point
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind configuration
├── scripts/
│   ├── docker-setup.sh     # Docker setup script
│   └── setup-postgres-local.sh # Local PostgreSQL setup
└── README.md               # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- PostgreSQL (for production) or SQLite (for development)

### Option 1: Docker Setup (Recommended)

1. **Run the setup script**:
   ```bash
   chmod +x scripts/docker-setup.sh
   ./scripts/docker-setup.sh
   ```

2. **Start the application**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development Setup

#### Backend Setup

1. **Set up PostgreSQL locally**:
   ```bash
   chmod +x scripts/setup-postgres-local.sh
   ./scripts/setup-postgres-local.sh
   ```

2. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

3. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Migrate from SQLite (if needed)**:
   ```bash
   python migrate_to_postgres.py
   ```

6. **Run the FastAPI server**:
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```
   
   The React app will be available at `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database (PostgreSQL)
DATABASE_URL=postgresql://news_user:news_password@localhost:5432/news_analyzer

# Security
SECRET_KEY=your-secret-key-change-in-production

# OpenAI API (optional - for AI features)
OPENAI_KEY=your_openai_api_key

# Environment
ENVIRONMENT=development
```

### Database Migration

If you have existing SQLite data and want to migrate to PostgreSQL:

1. **Run the migration script**:
   ```bash
   cd backend
   python migrate_to_postgres.py
   ```

2. **The script will**:
   - Check PostgreSQL connectivity
   - Backup existing SQLite data
   - Migrate data to PostgreSQL
   - Update environment configuration
   - Initialize the new database

### API Endpoints

#### Authentication
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout

#### Business Interests
- `GET /api/analysis/business-interest` - Get all business interests
- `POST /api/analysis/business-interest` - Create new business interest
- `GET /api/analysis/business-interest/{id}` - Get specific business interest
- `DELETE /api/analysis/business-interest/{id}` - Delete business interest

#### Sources
- `GET /api/sources/` - Get all sources
- `POST /api/sources/` - Add new source
- `DELETE /api/sources/{id}` - Remove source
- `GET /api/sources/popular` - Get popular sources

#### News Analysis
- `POST /api/news/analyze` - Analyze news
- `GET /api/news/sessions` - Get analysis sessions
- `GET /api/news/sessions/{id}` - Get specific session
- `DELETE /api/news/sessions/{id}` - Delete session

#### Statistics
- `GET /api/analysis/statistics` - Get user statistics
- `GET /api/analysis/dashboard` - Get dashboard data

## 🚀 Usage

1. **Start both servers** (backend and frontend)
2. **Open the application** at `http://localhost:3000` (local) or `http://localhost` (Docker)
3. **Login** with the demo account
4. **Set your business interest** on the Business Interest page
5. **Add news sources** on the Sources page
6. **Run analysis** on the Analysis page
7. **View results** on the Results page

## 🔄 Migration from Streamlit

The application has been successfully migrated from Streamlit to a modern React + FastAPI architecture:

### Key Improvements:
- **Better Performance**: React's virtual DOM and FastAPI's async capabilities
- **Enhanced UX**: Modern, responsive UI with real-time updates
- **Scalability**: RESTful API architecture for better scaling
- **Type Safety**: TypeScript for frontend, Pydantic for backend
- **State Management**: React Query for efficient server state management
- **Authentication**: Proper token-based authentication system
- **Database**: PostgreSQL for production-ready data storage

## 🗄️ Database Information

### PostgreSQL (Default)
- **Host**: localhost (local) / postgres (Docker)
- **Port**: 5432
- **Database**: news_analyzer
- **User**: news_user
- **Password**: news_password

### SQLite (Legacy/Development)
- **File**: `backend/db/analyzer.db`
- **Use**: Development fallback only

## 📊 Performance Benefits

### PostgreSQL Advantages:
- **Concurrent Users**: Support for multiple simultaneous users
- **Data Integrity**: ACID compliance and foreign key constraints
- **Scalability**: Better performance with large datasets
- **Backup & Recovery**: Robust backup and recovery options
- **Production Ready**: Enterprise-grade database solution

## 🧪 Testing

### Backend Testing
```