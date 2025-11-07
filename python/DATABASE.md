# Database Setup and Configuration

## Overview

The DiffRhythm service uses SQLAlchemy with SQLite as the default persistence layer for tracking jobs, tracks, and loops. The database is automatically initialized on application startup.

## Database Structure

### Models

The application defines three main models:

#### Job
Represents a music generation job with:
- `job_id`: Unique job identifier (UUID, primary key)
- `job_type`: Type of job (e.g., 'diffrhythm')
- `status`: Current status (pending, loading_model, preparing_prompt, generating_audio, exporting, completed, failed)
- `progress`: Progress percentage (0-100)
- `prompt`: Original text prompt
- `metadata`: JSON field containing language, genre, mood, etc.
- `file_manifest`: JSON field containing file paths and URLs
- `error`: Error message if job failed
- `created_at`: Timestamp when job was created
- `updated_at`: Timestamp of last update

#### Track
Represents a generated music track with:
- `track_id`: Unique track identifier (UUID, primary key)
- `job_id`: Foreign key to Job
- `duration`: Duration in seconds
- `metadata`: JSON field for artist, album, genre, track_name, etc.
- `file_path_wav`: Path to WAV file
- `file_path_mp3`: Path to MP3 file
- `created_at`: Timestamp when track was created
- `updated_at`: Timestamp of last update

#### Loop
Represents a looped variant of a track with:
- `loop_id`: Unique loop identifier (UUID, primary key)
- `track_id`: Foreign key to Track
- `status`: Current status (PENDING, ANALYZING, RENDERING, EXPORTING, COMPLETED, FAILED)
- `duration`: Loop duration in seconds
- `fade_in_out`: Boolean flag (0 or 1) for fade in/out
- `format`: Audio format (MP3, WAV)
- `progress`: Progress percentage (0-100)
- `error`: Error message if loop creation failed
- `result_url`: URL for downloading the loop
- `result_path`: File system path to the result
- `created_at`: Timestamp when loop was created
- `updated_at`: Timestamp of last update

### Relationships

- **Job → Track**: One-to-many (One job can have multiple tracks)
- **Track → Loop**: One-to-many (One track can have multiple loops)
- **Job → Loop** (through Track): Indirect relationship

Cascading deletes are configured:
- Deleting a Job automatically deletes all associated Tracks and their Loops
- Deleting a Track automatically deletes all associated Loops

## Configuration

### Environment Variables

Configure the database using environment variables:

```bash
# Database URL (optional, defaults to SQLite)
# Format: sqlite:///path/to/db.sqlite or postgresql://user:pass@host/dbname
export DATABASE_URL="sqlite:///./app.db"

# Database file path (only used if DATABASE_URL not set)
export DB_PATH="./app.db"

# Enable SQL logging (default: false)
export SQL_ECHO="false"
```

### Default Configuration

By default, the service uses SQLite at `./app.db` in the current working directory.

## Initialization

### Automatic Initialization

The database is automatically initialized when the FastAPI application starts. The startup event:
1. Creates all tables if they don't exist
2. Sets up relationships and foreign keys
3. Logs initialization success/failure

### Manual Initialization

To manually initialize the database:

```python
from app.database import init_database

init_database()
```

## Usage Examples

### Creating a Job

```python
from app.database import JobRepository, get_session

session = get_session()
repo = JobRepository(session)

job = repo.create(
    job_id="12345-67890",
    job_type="diffrhythm",
    status="pending",
    prompt="Generate ambient music",
    metadata={
        "language": "en",
        "genre": "ambient",
        "mood": "relaxing"
    }
)

session.close()
```

### Updating Job Status

```python
from app.database import JobRepository, get_session

session = get_session()
repo = JobRepository(session)

updated_job = repo.update(
    job_id="12345-67890",
    status="completed",
    progress=100,
    file_manifest={
        "wav_path": "/output/track.wav",
        "mp3_path": "/output/track.mp3"
    }
)

session.close()
```

### Retrieving Jobs

```python
from app.database import JobRepository, get_session

session = get_session()
repo = JobRepository(session)

# Get single job
job = repo.get_by_id("12345-67890")

# Get all pending jobs
pending_jobs = repo.get_by_status("pending")

# Get all jobs with pagination
all_jobs = repo.get_all(limit=50, offset=0)

session.close()
```

### Creating a Track

```python
from app.database import TrackRepository, get_session
import uuid

session = get_session()
repo = TrackRepository(session)

track = repo.create(
    track_id=str(uuid.uuid4()),
    job_id="12345-67890",
    duration=30.5,
    metadata={
        "artist": "AI Generated",
        "album": "Generated Tracks",
        "genre": "Ambient"
    },
    file_path_wav="/output/track.wav",
    file_path_mp3="/output/track.mp3"
)

session.close()
```

### Creating a Loop

```python
from app.database import LoopRepository, get_session
import uuid

session = get_session()
repo = LoopRepository(session)

loop = repo.create(
    loop_id=str(uuid.uuid4()),
    track_id="track-id-here",
    duration=120,
    fade_in_out=1,
    format="MP3",
    status="PENDING"
)

session.close()
```

## Testing

Run the database tests:

```bash
cd python
pytest tests/test_database.py -v
```

Test coverage includes:
- Model creation and persistence
- Field validation and defaults
- Relationships and foreign keys
- CRUD operations via repositories
- Cascading deletes
- JSON field handling

## Migration Strategy

Currently, the application uses a simple schema initialization approach:
- Tables are created automatically on startup if they don't exist
- No explicit migration files are needed for basic schema

For future enhancements with complex migrations, consider:
1. **Alembic**: Flask-style migrations with versioning
   ```bash
   # Initialize Alembic
   alembic init migrations
   
   # Auto-generate migration
   alembic revision --autogenerate -m "Add new column"
   
   # Apply migrations
   alembic upgrade head
   ```

2. **Manual migration script**: Create Python scripts for complex schema changes

## Performance Considerations

1. **Connection Pooling**: SQLAlchemy handles connection pooling automatically
2. **Indexes**: Consider adding indexes on frequently queried fields:
   - `job_id` on Track
   - `track_id` on Loop
   - `status` on Job and Loop

3. **Query Optimization**: Use pagination for large result sets
4. **In-Memory Cache**: The JobStore maintains an in-memory cache for frequently accessed jobs

## Backing Up Data

### SQLite

```bash
# Simple file copy
cp app.db app.db.backup

# Using sqlite3 command
sqlite3 app.db ".backup app.db.backup"
```

### PostgreSQL

```bash
# Using pg_dump
pg_dump -U username databasename > backup.sql

# Restore from backup
psql -U username databasename < backup.sql
```

## Troubleshooting

### Database File Not Found

**Error**: `sqlite3.OperationalError: unable to open database file`

**Solution**: Ensure the directory exists and you have write permissions:
```bash
mkdir -p ./output
chmod 755 ./output
```

### Database Locked

**Error**: `database is locked`

**Solution**: 
- Close other connections to the database
- Check for long-running queries
- Restart the application

### Foreign Key Violation

**Error**: `FOREIGN KEY constraint failed`

**Solution**: Ensure you're creating entities in the correct order (Job before Track before Loop)

## Production Recommendations

1. **Use PostgreSQL**: More suitable for production than SQLite
2. **Configure Connection Pool**: Adjust pool size based on load
3. **Enable Connection Encryption**: Use SSL for database connections
4. **Regular Backups**: Implement automated backup schedule
5. **Monitoring**: Monitor database performance and connection pool usage
6. **Indexes**: Add indexes on frequently queried fields
7. **Archival**: Archive old jobs/tracks to separate storage
