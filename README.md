# VectorDB Demo - Guitar Practice Routine Manager

A Flask-based web application that uses ChromaDB for managing and searching guitar practice routines with vector embeddings and semantic search capabilities.

## Features

- **Vector Database**: Uses ChromaDB for efficient storage and retrieval of practice routines
- **Semantic Search**: Search routines by text content using OpenAI embeddings
- **Category Filtering**: Filter routines by category (daily, one_day, two_three_days)
- **State Management**: Track completion status of practice routines
- **REST API**: Flask-based API for web integration
- **Interactive CLI**: Command-line interface for routine management

## Project Structure

```
vectorDb-demo/
├── app.py                          # Flask web API
├── chroma_db_manager.py            # Main CLI interface and database setup
├── build_chroma_db.py              # Database initialization and embedding generation
├── search_by_category.py           # Category-based search functionality
├── search_by_text.py               # Semantic text search
├── get_all_routines.py             # Retrieve all routines
├── get_not_completed_routines.py   # Get pending routines
├── mark_routine_completed.py       # Mark routines as completed
├── utils.py                        # Helper functions and display utilities
└── routines/
    └── routines.json               # Practice routine data
```

## Setup Instructions

### Prerequisites

- Python 3.7+
- OpenAI API key

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd vectorDb-demo
   ```

2. **Install dependencies**

   ```bash
   pip install flask flask-cors chromadb openai python-dotenv
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Initialize the database**
   ```bash
   python chroma_db_manager.py
   ```
   Select option `0` to build the database from the JSON file.

### Running the Application

#### Web API (Port 5050)

```bash
python app.py
```

The Flask API will start on `http://localhost:5050`

**Why Port 5050?**
This project uses port 5050 instead of the default Flask port 5000 due to a conflict with Apple's AirPlay Receiver service, which occupies port 5000 on macOS systems. Port 5050 provides a reliable alternative without system conflicts.

#### CLI Interface

```bash
python chroma_db_manager.py
```

This launches an interactive menu with the following options:

- `0` - Build/rebuild database
- `1` - Get all practice routines
- `2` - Search routines by category
- `3` - Search routines by text (semantic search)
- `4` - Get not-completed routines
- `5` - Mark a routine as completed
- `6` - Exit

## API Endpoints

### GET /api/random-routine

Returns a random practice routine from the specified category.

**Parameters:**

- `category` (required): Filter by category (`daily`, `one_day`, `two_three_days`)
- `state` (optional): Filter by completion state (default: `not_completed`)

**Example:**

```bash
curl "http://localhost:5050/api/random-routine?category=daily"
```

**Response:**

```json
{
  "message": "Ear training using major scales"
}
```

**Error Responses:**

- `400`: Missing category parameter
- `404`: No routines found for the specified category/state

## Data Format

Practice routines are stored in `routines/routines.json` with the following structure:

```json
{
  "text": "Practice routine description",
  "category": "daily|one_day|two_three_days",
  "tags": ["tag1", "tag2"],
  "state": "not_completed|completed"
}
```

## Database Storage

- **ChromaDB**: Persistent storage in `../data/chroma_data/` directory
- **Collection**: `guitar_routines`
- **Embeddings**: Generated using OpenAI's text embedding models
- **Metadata**: Category, tags, and completion state for filtering

## Development

### Adding New Routines

1. Edit `routines/routines.json` to add new practice routines
2. Rebuild the database using option `0` in the CLI interface
3. The new routines will be automatically embedded and indexed

### Testing

Run a quick test to verify ChromaDB connectivity:

```bash
python -c "
from search_by_category import search_by_category
results = search_by_category('daily')
print(f'Found {len(results[\"documents\"])} routines')
"
```

## Dependencies

- **Flask**: Web framework for the API
- **Flask-CORS**: Cross-origin resource sharing support
- **ChromaDB**: Vector database for embeddings and search
- **OpenAI**: API for generating text embeddings
- **python-dotenv**: Environment variable management

## Port Information

This application runs on **port 5050** to avoid conflicts with:

- Apple's AirPlay Receiver (port 5000)
- Other common development services

If you need to change the port, modify line 27 in `app.py`:

```python
app.run(debug=True, port=5050)  # Change 5050 to your desired port
```
