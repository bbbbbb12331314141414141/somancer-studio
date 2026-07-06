# Somancer Studio — API Reference

## Overview

Base URL: `http://localhost:8000/api/v1`

All responses are JSON. Timestamps are ISO 8601 format (UTC).

---

## Health & Status

### Health Check
```
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "version": "0.0.1",
  "database": "connected",
  "ollama": "ready"
}
```

---

## Projects

### List All Projects
```
GET /projects
```

**Query Parameters:**
- `skip` (int, default: 0) — Pagination offset
- `limit` (int, default: 50) — Items per page
- `archived` (bool) — Filter by archived status

**Response (200):**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Debut Album 2024",
      "slug": "debut-album-2024",
      "description": "My first full-length album",
      "project_type": "album",
      "genre": "Neo-Soul",
      "artist_name": "Artist Name",
      "bpm": 90,
      "key": "D Major",
      "created_at": "2024-06-01T10:00:00Z",
      "updated_at": "2024-06-15T14:30:00Z",
      "archived": false,
      "cover_art_path": "/media/covers/album1.jpg",
      "metadata": {}
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 50
}
```

---

### Get Project by ID
```
GET /projects/{project_id}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Debut Album 2024",
  "slug": "debut-album-2024",
  "description": "My first full-length album",
  "project_type": "album",
  "genre": "Neo-Soul",
  "artist_name": "Artist Name",
  "bpm": 90,
  "key": "D Major",
  "created_at": "2024-06-01T10:00:00Z",
  "updated_at": "2024-06-15T14:30:00Z",
  "archived": false,
  "cover_art_path": "/media/covers/album1.jpg",
  "songs": [
    {
      "id": 5,
      "name": "Lost in the Night",
      "position": 1,
      "duration_seconds": 245.5
    }
  ],
  "metadata": {}
}
```

---

### Create Project
```
POST /projects
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Summer EP",
  "project_type": "ep",
  "description": "Three songs from summer 2024",
  "genre": "Indie Pop",
  "artist_name": "My Band",
  "bpm": 120,
  "key": "G Major"
}
```

**Response (201):**
```json
{
  "id": 6,
  "name": "Summer EP",
  "slug": "summer-ep",
  "project_type": "ep",
  "description": "Three songs from summer 2024",
  "genre": "Indie Pop",
  "artist_name": "My Band",
  "bpm": 120,
  "key": "G Major",
  "created_at": "2024-06-29T15:00:00Z",
  "updated_at": "2024-06-29T15:00:00Z",
  "archived": false,
  "metadata": {}
}
```

---

### Update Project
```
PATCH /projects/{project_id}
Content-Type: application/json
```

**Request (partial update):**
```json
{
  "name": "Summer EP (Deluxe)",
  "bpm": 125
}
```

**Response (200):** Updated project object

---

### Delete Project
```
DELETE /projects/{project_id}
```

**Response (204):** No content

---

## Songs

### List Songs in Project
```
GET /projects/{project_id}/songs
```

**Query Parameters:**
- `skip` (int)
- `limit` (int)

**Response (200):**
```json
{
  "songs": [
    {
      "id": 5,
      "project_id": 1,
      "name": "Lost in the Night",
      "position": 1,
      "duration_seconds": 245.5,
      "created_at": "2024-06-10T12:00:00Z",
      "updated_at": "2024-06-10T12:00:00Z",
      "metadata": {}
    },
    {
      "id": 6,
      "project_id": 1,
      "name": "Daylight Returns",
      "position": 2,
      "duration_seconds": 198.0,
      "created_at": "2024-06-11T09:30:00Z",
      "updated_at": "2024-06-11T09:30:00Z",
      "metadata": {}
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 50
}
```

---

### Get Song by ID
```
GET /songs/{song_id}
```

**Response (200):**
```json
{
  "id": 5,
  "project_id": 1,
  "name": "Lost in the Night",
  "position": 1,
  "duration_seconds": 245.5,
  "created_at": "2024-06-10T12:00:00Z",
  "updated_at": "2024-06-10T12:00:00Z",
  "tracks": [
    {
      "id": 15,
      "name": "Vocal",
      "track_type": "audio",
      "instrument": "Vocals",
      "volume": 1.0,
      "pan": 0.0,
      "muted": false
    }
  ],
  "lyrics": [],
  "metadata": {}
}
```

---

### Create Song
```
POST /projects/{project_id}/songs
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Echoes",
  "position": 1
}
```

**Response (201):** Created song object

---

## Lyrics

### Get Song Lyrics
```
GET /songs/{song_id}/lyrics
```

**Query Parameters:**
- `section` (string) — Filter by "verse", "chorus", "bridge", etc.

**Response (200):**
```json
{
  "lyrics": [
    {
      "id": 1,
      "song_id": 5,
      "line_number": 1,
      "section": "verse",
      "text": "I'm wandering through the darkness",
      "start_time_seconds": 0.0,
      "end_time_seconds": 4.5,
      "mood": "introspective",
      "language": "en"
    },
    {
      "id": 2,
      "song_id": 5,
      "line_number": 2,
      "section": "verse",
      "text": "Looking for a light to guide me",
      "start_time_seconds": 4.5,
      "end_time_seconds": 9.0,
      "mood": "introspective",
      "language": "en"
    }
  ],
  "total": 2
}
```

---

### Generate Lyrics (AI)
```
POST /ai/lyrics
Content-Type: application/json
```

**Request:**
```json
{
  "song_id": 5,
  "section": "verse",
  "count": 4,
  "mood": "romantic",
  "theme": "love",
  "vocabulary": "poetic",
  "language": "en",
  "length": "medium"
}
```

**Response (200):**
```json
{
  "lyrics": [
    {
      "line_number": 1,
      "section": "verse",
      "text": "Your love is like a melody",
      "mood": "romantic",
      "language": "en"
    },
    {
      "line_number": 2,
      "section": "verse",
      "text": "Dancing through my thoughts",
      "mood": "romantic",
      "language": "en"
    }
  ],
  "agent": "songwriter",
  "model": "mistral"
}
```

---

### Add Lyrics
```
POST /songs/{song_id}/lyrics
Content-Type: application/json
```

**Request:**
```json
{
  "line_number": 3,
  "section": "verse",
  "text": "A symphony of stars above",
  "mood": "romantic",
  "language": "en"
}
```

**Response (201):** Created lyric object

---

## Genres

### List All Genres
```
GET /genres
```

**Query Parameters:**
- `parent_id` (int) — Filter by parent genre
- `search` (string) — Search by name

**Response (200):**
```json
{
  "genres": [
    {
      "id": 1,
      "name": "Rock",
      "parent_id": null,
      "description": "Rock music...",
      "bpm_min": 80,
      "bpm_max": 140,
      "common_keys": ["E Major", "A Major", "D Major"],
      "common_instruments": ["Electric Guitar", "Bass", "Drums"],
      "typical_chord_progressions": ["I-V-vi-IV", "I-IV-V"],
      "production_techniques": ["Distortion", "Power Chords"],
      "vocal_style": "Powerful, expressive",
      "sources": ["Wikipedia", "Production Manual"]
    },
    {
      "id": 2,
      "name": "Hard Rock",
      "parent_id": 1,
      "description": "Hard rock subgenre...",
      "bpm_min": 100,
      "bpm_max": 160,
      "common_keys": ["E Major", "A Major"],
      "common_instruments": ["Distorted Guitar", "Bass", "Drums"],
      "typical_chord_progressions": ["I-V", "I-IV-V"],
      "production_techniques": ["Heavy Distortion", "Reverb"],
      "vocal_style": "Aggressive, powerful",
      "sources": ["Wikipedia"]
    }
  ],
  "total": 200
}
```

---

### Get Genre by ID
```
GET /genres/{genre_id}
```

**Response (200):** Genre object (see List above)

---

## AI Models

### List Available Models
```
GET /models
```

**Query Parameters:**
- `model_type` (string) — Filter by "text", "music", "voice", "image"
- `provider` (string) — Filter by "ollama", "anthropic", "openai"
- `local_only` (bool) — Show only local models

**Response (200):**
```json
{
  "models": [
    {
      "id": 1,
      "name": "Mistral 7B",
      "model_type": "text",
      "provider": "ollama",
      "model_id": "mistral",
      "version": "latest",
      "local": true,
      "enabled": true,
      "size_gb": 4.4,
      "parameters": {
        "temperature": 0.7,
        "top_p": 0.9
      },
      "downloaded_at": "2024-06-25T10:00:00Z",
      "last_used": "2024-06-29T14:00:00Z"
    },
    {
      "id": 2,
      "name": "Llama 2 70B",
      "model_type": "text",
      "provider": "ollama",
      "model_id": "llama2",
      "version": "latest",
      "local": false,
      "enabled": true,
      "size_gb": 38.5,
      "parameters": {},
      "downloaded_at": null,
      "last_used": null
    }
  ],
  "total": 2
}
```

---

### Download Model
```
POST /models/{model_id}/download
```

**Response (202):** Accepted (async operation)
```json
{
  "job_id": "job_abc123",
  "model_id": 2,
  "status": "downloading",
  "progress": 0.0
}
```

---

## Jobs (Background Tasks)

### List Jobs
```
GET /jobs
```

**Query Parameters:**
- `song_id` (int)
- `status` (string) — "pending", "running", "completed", "failed"
- `skip`, `limit` — Pagination

**Response (200):**
```json
{
  "jobs": [
    {
      "id": 42,
      "song_id": 5,
      "job_type": "render",
      "status": "running",
      "progress": 0.65,
      "result_path": null,
      "error_message": null,
      "created_at": "2024-06-29T14:00:00Z",
      "started_at": "2024-06-29T14:01:00Z",
      "completed_at": null
    }
  ],
  "total": 1
}
```

---

### Get Job Status
```
GET /jobs/{job_id}
```

**Response (200):** Job object (see List above)

---

### Cancel Job
```
POST /jobs/{job_id}/cancel
```

**Response (200):**
```json
{
  "id": 42,
  "status": "cancelled"
}
```

---

## Audio Rendering

### Render Song
```
POST /audio/render
Content-Type: application/json
```

**Request:**
```json
{
  "song_id": 5,
  "format": "wav",
  "sample_rate": 48000,
  "bit_depth": 24
}
```

**Response (202):** Accepted
```json
{
  "job_id": "job_render_001",
  "song_id": 5,
  "status": "pending",
  "progress": 0.0,
  "estimated_seconds": 120
}
```

---

## Exports

### List Exports
```
GET /exports
```

**Query Parameters:**
- `project_id` (int)
- `format` (string)
- `skip`, `limit`

**Response (200):**
```json
{
  "exports": [
    {
      "id": 1,
      "project_id": 1,
      "format": "wav",
      "quality": "hq",
      "file_path": "/exports/debut-album-2024_master.wav",
      "file_size_mb": 450.5,
      "created_at": "2024-06-28T16:00:00Z",
      "exported_by": "Sonmancer v0.0.1"
    }
  ],
  "total": 1
}
```

---

### Export Project
```
POST /projects/{project_id}/export
Content-Type: application/json
```

**Request:**
```json
{
  "format": "mp3",
  "quality": "standard",
  "include_stems": false
}
```

**Response (202):** Accepted
```json
{
  "job_id": "job_export_001",
  "project_id": 1,
  "format": "mp3",
  "status": "pending"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "details": [
    {
      "field": "name",
      "message": "Name must be 1-255 characters"
    }
  ]
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "resource": "song",
  "id": 999
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req_xyz789"
}
```

---

## Pagination

All list endpoints support:
- `skip` (int, default: 0)
- `limit` (int, default: 50, max: 500)

Response includes:
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

---

## Rate Limiting (Future)

All endpoints will be rate-limited (Phase 1+):
- 1000 requests/hour (per user)
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## WebSocket (Future)

Real-time job progress updates (Phase 2+):
```
GET /ws/jobs/{job_id}
```

Message format:
```json
{
  "type": "progress",
  "job_id": "job_render_001",
  "status": "running",
  "progress": 0.75,
  "eta_seconds": 15
}
```

