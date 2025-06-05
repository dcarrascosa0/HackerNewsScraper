# Hacker News Scraper API

A fast, asynchronous API that scrapes and serves Hacker News articles with intelligent caching.

## 🚀 Features

- **Asynchronous API** built with FastAPI
- **Web scraping** of Hacker News front page using BeautifulSoup
- **Intelligent caching** to minimize redundant requests
- **Docker support** for consistent deployment
- **Comprehensive test suite** following TDD methodology
- **Concurrent fetching** for optimal performance

## 📋 Requirements

- Python 3.10+
- Docker & Docker Compose (for containerized deployment)

## 🛠 Installation & Setup

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/dcarrascosa0/HackerNewsScraper
   cd HackerNewsScraper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate    # Linux/macOS
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/dcarrascosa0/HackerNewsScraper
   cd HackerNewsScraper
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## 🏃‍♂️ Running the API

### Local Development
```bash
# Activate virtual environment first
uvicorn app.main:app --reload --port 3000
```

### Docker
```bash
# Start the API service
docker-compose up

# Or run in detached mode
docker-compose up -d
```

The API will be available at `http://localhost:3000`

## 🧪 Running Tests

### Local Testing
```bash
# Activate virtual environment first
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py
pytest tests/test_scraper.py  
pytest tests/test_cache.py
```

### Docker Testing
```bash
# Run tests in Docker container
docker-compose --profile test run test

# Or run tests with verbose output
docker-compose --profile test run test pytest -v
```

## 📚 API Documentation

### Endpoints

#### `GET /`
Returns the first page (30 items) from Hacker News front page.

**Response**: Array of 30 news objects

#### `GET /{number}`
Returns the specified number of pages from Hacker News.

**Parameters:**
- `number` (integer): Number of pages to fetch (must be ≥ 1)

**Examples:**
- `GET /1` → Returns 30 items (page 1)
- `GET /2` → Returns 60 items (pages 1-2) 
- `GET /5` → Returns 150 items (pages 1-5)

**Response Format:**
```json
[
  {
    "title": "Example Article Title",
    "url": "https://example.com/article",
    "points": 125,
    "sent_by": "username",
    "published": "2 hours ago",
    "comments": 42
  }
]
```

### Error Responses

- `400 Bad Request`: Invalid page number (< 1)
- `422 Unprocessable Entity`: Invalid parameter type
- `500 Internal Server Error`: Network or parsing errors

## 🏗 Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── scraper.py       # Web scraping logic
│   └── cache.py         # In-memory caching system
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # API endpoint tests
│   ├── test_scraper.py  # Scraper functionality tests
│   └── test_cache.py    # Cache mechanism tests
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-service orchestration
├── requirements.txt     # Python dependencies
├── pytest.ini         # Test configuration
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🧠 How It Works

### Caching Strategy
The API implements intelligent caching to optimize performance:

- **Cache Hit**: If requested pages are already cached, returns immediately
- **Partial Cache**: Fetches only missing pages and combines with cached data
- **Cache Miss**: Fetches all required pages concurrently

**Example Scenarios:**
1. Request `/1` → Fetches page 1, caches it
2. Request `/3` → Fetches pages 2-3 (page 1 already cached)
3. Request `/2` → Returns from cache (pages 1-2 already available)

### Web Scraping
- Scrapes `https://news.ycombinator.com/news?p={page}`
- Extracts: title, URL, points, author, publish time, comment count
- Handles edge cases: deleted users, missing data, etc.

## 🔧 Development

### Running in Development Mode
```bash
# With auto-reload
uvicorn app.main:app --reload --port 3000

# With Docker (includes volume mounting for live reload)
docker-compose up
```

### Testing Strategy
The project follows **Test-Driven Development (TDD)**:

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing with mocked scraper
- **Edge Case Testing**: Invalid inputs, network errors, etc.
