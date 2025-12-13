# Practice Routines API - New Architecture

## Overview

The codebase has been reorganized into a clean, layered architecture following industry best practices. This structure provides better separation of concerns, testability, and maintainability.

## Directory Structure

```
practice-routines-api/
├── app.py                      # Flask API entry point
├── cli.py                      # CLI entry point
├── .env.example                # Environment variables template
├── routines/
│   └── routines.json          # Practice routines data
├── data/
│   └── chroma_data/           # ChromaDB storage
└── src/
    ├── api/
    │   ├── app_factory.py     # Flask application factory
    │   └── routes.py          # API endpoints
    ├── services/
    │   ├── routine_service.py # Business logic
    │   └── embedding_service.py # OpenAI embeddings
    ├── repositories/
    │   └── routine_repository.py # ChromaDB data access
    ├── models/
    │   └── routine.py         # Data models
    ├── config/
    │   ├── settings.py        # Configuration
    │   └── database.py        # Database client management
    └── cli/
        ├── commands.py        # CLI command handlers
        ├── display.py         # CLI output formatting
        └── database_commands.py # Database build operations
```

## Architecture Layers

### 1. **Models Layer** (`src/models/`)

Defines data structures and validation.

- `Routine`: Represents a practice routine with validation
- `RoutineSearchResult`: Search results with metadata and scores

**Key Features:**
- Type-safe data classes using `@dataclass`
- Automatic validation in `__post_init__`
- Conversion methods (`from_dict`, `to_dict`, `from_chroma_result`)

### 2. **Repository Layer** (`src/repositories/`)

Handles all database interactions with ChromaDB.

**RoutineRepository** provides:
- `get_all()`: Fetch all routines
- `get_by_category(category, state)`: Filter by category/state
- `get_by_state(state)`: Filter by completion state
- `search_by_embedding(embedding, top_n)`: Semantic search
- `update_metadata(id, metadata)`: Update routine metadata
- `get_by_id(id)`: Fetch single routine

**Benefits:**
- All ChromaDB queries in one place
- Proper error handling and logging
- Easy to mock for testing

### 3. **Services Layer** (`src/services/`)

Contains business logic and coordinates between layers.

**EmbeddingService:**
- `generate_embedding(text)`: Single text embedding
- `generate_embeddings_batch(texts)`: Batch embedding generation
- Handles OpenAI API errors

**RoutineService:**
- `get_all_routines()`: Get all routines
- `get_routines_by_category(category, state)`: Filtered search
- `get_random_routine_by_category(category, state)`: Random selection
- `get_not_completed_routines()`: Uncompleted routines
- `search_routines(query, top_n, min_score)`: Semantic search
- `mark_routine_completed(id)`: Mark as done
- `mark_routine_not_completed(id)`: Mark as not done

**Benefits:**
- Business logic separated from data access
- Easy to add new features
- Testable without database

### 4. **API Layer** (`src/api/`)

Flask REST API endpoints.

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/get-random-routine-by-category-state` | Get random routine (legacy endpoint) |
| GET | `/api/routines` | Get all routines with optional filters |
| GET | `/api/routines/search` | Semantic search |
| PUT | `/api/routines/<id>/complete` | Mark routine completed |
| PUT | `/api/routines/<id>/uncomplete` | Mark routine not completed |

**app_factory.py:**
- Creates Flask app with dependency injection
- Initializes all layers
- Configures CORS and logging
- Registers blueprints

**Benefits:**
- Clean separation of routes and business logic
- Easy to add new endpoints
- Dependency injection for testing

### 5. **CLI Layer** (`src/cli/`)

Interactive command-line interface.

**Commands:**
- Build database from JSON file
- Get all routines
- Search by category
- Semantic text search
- Get not-completed routines
- Mark routine as completed

**Benefits:**
- User-friendly menu interface
- Comprehensive error handling
- Pretty output formatting

### 6. **Config Layer** (`src/config/`)

Configuration and database client management.

**settings.py:**
- Environment-based configuration (dev/prod)
- All settings from environment variables
- `.env.example` template provided

**database.py:**
- Singleton pattern for ChromaDB client
- Singleton pattern for OpenAI client
- Lazy initialization
- Error handling and logging

## Key Improvements

### 1. **Separation of Concerns**
Each layer has a single responsibility:
- Models: Data structure
- Repositories: Data access
- Services: Business logic
- API: HTTP handling
- CLI: User interaction

### 2. **Dependency Injection**
Components receive dependencies through constructors, making them:
- Testable (easy to mock)
- Flexible (easy to swap implementations)
- Clear about dependencies

### 3. **Error Handling**
- Each layer validates inputs
- Specific exception types (`ValueError`, `RuntimeError`)
- Exception chaining preserves stack traces
- Comprehensive logging at all levels

### 4. **Type Safety**
- Type hints throughout
- Data classes for models
- Clear interfaces between layers

### 5. **Testability**
- Each layer can be tested independently
- Easy to mock dependencies
- Repository layer isolates database access

## Usage

### Running the API

```bash
python app.py
```

The app will:
1. Load configuration from `.env`
2. Initialize database connections
3. Create all service layers
4. Start Flask server on configured host/port

### Running the CLI

```bash
python cli.py
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
FLASK_ENV=development
DEBUG=True
OPENAI_API_KEY=your-key-here
CHROMA_DB_PATH=../data/chroma_data
COLLECTION_NAME=guitar_routines
EMBEDDING_MODEL=text-embedding-3-small
FLASK_HOST=127.0.0.1
FLASK_PORT=5050
CORS_ORIGINS=*
ROUTINES_FILE=routines/routines.json
```

## Migration Notes

### Old vs New

**Old Structure:**
```
app.py (routes + logic)
search_by_category.py
search_by_text.py
get_all_routines.py
mark_routine_completed.py
...
```

**New Structure:**
```
src/
  api/routes.py (just routes)
  services/routine_service.py (all logic)
  repositories/routine_repository.py (all data access)
```

### Benefits of New Structure

1. **Single Responsibility**: Each file does one thing
2. **No Duplication**: Shared logic in services
3. **Easy Testing**: Mock at layer boundaries
4. **Clear Dependencies**: Explicit constructor injection
5. **Better Organization**: Find code by layer, not by feature

## Next Steps

1. **Add Unit Tests**: Test each layer independently
2. **Add Integration Tests**: Test full request flow
3. **Add API Documentation**: OpenAPI/Swagger
4. **Add Authentication**: JWT or API keys
5. **Add More Endpoints**: CRUD operations for routines
6. **Add Database Migrations**: Version control for schema

## Code Examples

### Adding a New Endpoint

```python
# In src/api/routes.py
@api_bp.route("/routines/<routine_id>", methods=["GET"])
def get_routine(routine_id):
    try:
        routine = _routine_service.get_routine_by_id(routine_id)
        if not routine:
            return jsonify({"error": "Routine not found"}), 404
        return jsonify(routine.to_dict())
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": "Server error"}), 500
```

### Adding Business Logic

```python
# In src/services/routine_service.py
def get_routine_by_id(self, routine_id: str) -> Optional[RoutineSearchResult]:
    """Get a single routine by ID."""
    result = self.repository.get_by_id(routine_id)
    if not result:
        return None
    return RoutineSearchResult.from_chroma_result(
        result["id"],
        result["document"],
        result["metadata"]
    )
```

## Testing

The architecture makes testing straightforward:

```python
# Test repository with mock ChromaDB
mock_collection = Mock()
repo = RoutineRepository(mock_collection)

# Test service with mock repository
mock_repo = Mock()
mock_embedding = Mock()
service = RoutineService(mock_repo, mock_embedding)

# Test API with test client
app = create_app()
with app.test_client() as client:
    response = client.get('/api/routines')
```

## Performance

- **Singleton Clients**: Database clients created once
- **Batch Embeddings**: Process multiple texts together
- **Lazy Loading**: Initialize only when needed
- **Indexed Queries**: ChromaDB metadata filtering

## Security

- **Input Validation**: All layers validate inputs
- **Error Messages**: Don't leak sensitive info
- **CORS**: Configurable allowed origins
- **Env Variables**: Secrets not in code

---

**Generated as part of the refactoring to clean architecture pattern**
