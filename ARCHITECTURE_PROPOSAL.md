# News Analyzer: React + FastAPI Architecture Proposal

## Current vs Proposed Architecture

### Current (Streamlit)
```
User → Streamlit App → Scrapy Spider → LLM Processing → Results
```

### Proposed (React + FastAPI)
```
User → React App → FastAPI Backend → Scrapy Spider → LLM Processing → Results
                ↓
            WebSocket/SSE for real-time updates
```

## Performance Improvements

### 1. **Non-blocking UI Operations**
- **Current**: UI freezes during 30-60 second scraping
- **Proposed**: Background processing with real-time progress updates

### 2. **Concurrent Processing**
- **Current**: Single-threaded, one request at a time
- **Proposed**: Async FastAPI with multiple concurrent scraping jobs

### 3. **Client-side Caching**
- **Current**: Server-side session state only
- **Proposed**: React state + localStorage for instant navigation

### 4. **Real-time Updates**
- **Current**: No progress indication
- **Proposed**: Live progress bars, article counts, status updates

## Technical Implementation

### Backend (FastAPI)

```python
# main.py
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/scrape")
async def start_scraping(sources: List[str], business_interest: str, background_tasks: BackgroundTasks):
    # Start background scraping job
    task_id = generate_task_id()
    background_tasks.add_task(scrape_articles, task_id, sources, business_interest)
    return {"task_id": task_id, "status": "started"}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    # Send real-time updates during scraping
    while True:
        progress = get_progress(task_id)
        await websocket.send_json(progress)
        await asyncio.sleep(1)

@app.get("/api/results/{task_id}")
async def get_results(task_id: str):
    return get_cached_results(task_id)
```

### Frontend (React)

```jsx
// App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import BusinessInterest from './components/BusinessInterest';
import SourceSelection from './components/SourceSelection';
import Results from './components/Results';

function App() {
  const [currentStep, setCurrentStep] = useState('business-interest');
  const [businessInterest, setBusinessInterest] = useState('');
  const [selectedSources, setSelectedSources] = useState([]);
  const [scrapingProgress, setScrapingProgress] = useState(null);

  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar currentStep={currentStep} />
        <main>
          <Routes>
            <Route path="/" element={
              <BusinessInterest 
                value={businessInterest}
                onChange={setBusinessInterest}
                onNext={() => setCurrentStep('sources')}
              />
            } />
            <Route path="/sources" element={
              <SourceSelection 
                selected={selectedSources}
                onChange={setSelectedSources}
                onNext={() => setCurrentStep('results')}
              />
            } />
            <Route path="/results" element={
              <Results 
                businessInterest={businessInterest}
                sources={selectedSources}
                progress={scrapingProgress}
              />
            } />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
```

## Performance Metrics Comparison

| Metric | Current (Streamlit) | Proposed (React+FastAPI) |
|--------|-------------------|-------------------------|
| **Initial Load Time** | 2-3 seconds | < 1 second |
| **UI Responsiveness** | Freezes during scraping | Always responsive |
| **Concurrent Users** | 1-2 | 10-50+ |
| **Memory Usage** | High (server-side state) | Lower (distributed) |
| **Error Recovery** | Page refresh required | Graceful retry |
| **Real-time Updates** | None | Live progress |

## Migration Strategy

### Phase 1: Backend API Development
1. Create FastAPI endpoints for existing functionality
2. Implement WebSocket for real-time updates
3. Add background task processing
4. Migrate database operations

### Phase 2: Frontend Development
1. Create React components for each page
2. Implement state management (Redux/Context)
3. Add real-time progress indicators
4. Implement client-side caching

### Phase 3: Integration & Testing
1. Connect frontend to backend APIs
2. Test real-time updates
3. Performance optimization
4. Deployment setup

## Expected Performance Gains

### User Experience
- **90% reduction** in perceived loading time
- **Real-time progress** during scraping operations
- **Instant navigation** between pages
- **Better error handling** with retry mechanisms

### System Performance
- **5-10x improvement** in concurrent user capacity
- **50% reduction** in server memory usage
- **Better scalability** for horizontal deployment
- **Improved caching** strategies

## Development Timeline

- **Week 1-2**: FastAPI backend development
- **Week 3-4**: React frontend development  
- **Week 5**: Integration and testing
- **Week 6**: Performance optimization and deployment

## Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **WebSockets**: Real-time communication
- **Celery**: Background task processing
- **Redis**: Caching and message broker
- **SQLAlchemy**: Database ORM

### Frontend
- **React 18**: Modern UI framework
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Tailwind CSS**: Utility-first styling
- **React Query**: Server state management

### Deployment
- **Docker**: Containerization
- **Nginx**: Reverse proxy
- **Gunicorn**: WSGI server
- **Vercel/Netlify**: Frontend hosting

## Conclusion

Migrating to React + FastAPI would provide:
- **Significantly better performance**
- **Improved user experience**
- **Better scalability**
- **Modern development practices**
- **Easier maintenance and updates**

The investment in migration would pay off quickly through improved user satisfaction and system reliability. 