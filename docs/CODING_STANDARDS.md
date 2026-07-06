# Somancer Studio — Coding Standards

## General Principles

1. **Readability > Cleverness** — Write code for humans, not compilers
2. **Type Safety** — Use TypeScript (frontend) and Python type hints (backend)
3. **Consistency** — Follow established patterns in codebase
4. **Testing** — Test-driven development for critical paths
5. **Documentation** — Self-documenting code + docstrings for complex logic
6. **DRY** — Don't Repeat Yourself; extract common patterns

---

## TypeScript / Frontend

### File Organization

```
packages/desktop/src/
├── components/          # Reusable React components
│   ├── Button.tsx
│   ├── Dialog.tsx
│   └── forms/           # Form-specific components
├── pages/               # Page-level components (one per route)
│   ├── Dashboard.tsx
│   ├── ProjectEditor.tsx
│   └── Settings.tsx
├── hooks/               # Custom React hooks
│   ├── useProjects.ts
│   ├── useLyrics.ts
│   └── useAudio.ts
├── services/            # API client functions
│   ├── api.ts
│   ├── projectService.ts
│   ├── lyricService.ts
│   └── audioService.ts
├── types/               # TypeScript type definitions
│   ├── index.ts
│   ├── project.ts
│   ├── song.ts
│   └── api.ts
├── utils/               # Utility functions
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
├── context/             # React Context providers
│   └── ProjectContext.tsx
├── App.tsx              # Root component
└── main.tsx             # Entry point
```

### Naming Conventions

| Artifact | Convention | Example |
| --- | --- | --- |
| Components | PascalCase | `ProjectEditor.tsx` |
| Functions | camelCase | `formatBPM()` |
| Constants | UPPER_SNAKE_CASE | `MAX_PROJECT_NAME_LENGTH` |
| Types | PascalCase | `type ProjectInput = {...}` |
| Files (components) | PascalCase | `ProjectList.tsx` |
| Files (utilities) | camelCase | `formatters.ts` |
| Boolean variables | `is*`, `has*`, `should*` | `isLoading`, `hasError` |

### Component Structure

```typescript
import { FC, useState, useCallback } from 'react';
import { Box, Button } from '@mui/material';
import { useProjects } from '../hooks/useProjects';
import { Project } from '../types';

interface ProjectListProps {
  onSelectProject: (project: Project) => void;
}

/**
 * ProjectList displays all user projects with creation and selection.
 */
export const ProjectList: FC<ProjectListProps> = ({ onSelectProject }) => {
  const [filter, setFilter] = useState('');
  const { projects, loading, error } = useProjects();

  const handleSelect = useCallback(
    (project: Project) => {
      onSelectProject(project);
    },
    [onSelectProject]
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <Box>
      {/* JSX */}
    </Box>
  );
};
```

### Type Safety

```typescript
// ✅ Good: Explicit typing
interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message: string;
}

async function fetchProjects(): Promise<Project[]> {
  const response = await api.get<ApiResponse<Project[]>>('/projects');
  return response.data.data;
}

// ❌ Bad: `any` type
async function fetchProjects(): Promise<any> {
  const response = await api.get('/projects');
  return response.data;
}
```

### Async/Await

```typescript
// ✅ Good: Error handling
async function loadProject(projectId: number): Promise<void> {
  try {
    const project = await projectService.getProject(projectId);
    setProject(project);
  } catch (error) {
    if (error instanceof ApiError) {
      setError(`Failed to load project: ${error.message}`);
    } else {
      setError('An unexpected error occurred');
    }
  }
}

// ❌ Bad: No error handling
async function loadProject(projectId: number): Promise<void> {
  const project = await projectService.getProject(projectId);
  setProject(project);
}
```

### Hooks Best Practices

```typescript
// ✅ Good: Proper dependencies
const handleCreate = useCallback(
  (name: string) => {
    createProject(name, selectedGenre); // selectedGenre is included
  },
  [selectedGenre] // dependency array includes all deps
);

// ❌ Bad: Missing dependencies
const handleCreate = useCallback(
  (name: string) => {
    createProject(name, selectedGenre); // selectedGenre changes, but not in deps!
  },
  []
);
```

### API Calls

```typescript
// services/projectService.ts

import axios, { AxiosError } from 'axios';
import { Project, CreateProjectInput } from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: Record<string, string>
  ) {
    super(message);
  }
}

export async function listProjects(skip = 0, limit = 50): Promise<Project[]> {
  try {
    const response = await axios.get<{ projects: Project[]; total: number }>(
      `${API_BASE}/projects`,
      { params: { skip, limit } }
    );
    return response.data.projects;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new ApiError(
        error.response.status,
        error.response.data.error || 'Unknown error',
        error.response.data.details
      );
    }
    throw new ApiError(0, 'Network error');
  }
}

export async function createProject(input: CreateProjectInput): Promise<Project> {
  const response = await axios.post<Project>(`${API_BASE}/projects`, input);
  return response.data;
}
```

---

## Python / Backend

### File Organization

```
packages/backend/aimusic/
├── api/                 # FastAPI routers
│   ├── __init__.py
│   ├── projects.py
│   ├── songs.py
│   ├── lyrics.py
│   ├── ai.py
│   ├── audio.py
│   └── health.py
├── services/            # Business logic
│   ├── __init__.py
│   ├── project_service.py
│   ├── song_service.py
│   ├── ai_service.py
│   ├── audio_service.py
│   └── plugin_service.py
├── models/              # SQLAlchemy ORM models
│   ├── __init__.py
│   └── entities.py
├── schemas/             # Pydantic request/response models
│   ├── __init__.py
│   ├── project.py
│   ├── song.py
│   ├── lyrics.py
│   └── common.py
├── utils/               # Helper functions
│   ├── __init__.py
│   ├── audio.py
│   ├── validators.py
│   └── decorators.py
├── config.py            # Configuration
├── db.py                # Database connection
└── main.py              # FastAPI app
```

### Naming Conventions

| Artifact | Convention | Example |
| --- | --- | --- |
| Files | snake_case | `project_service.py` |
| Classes | PascalCase | `ProjectService` |
| Functions | snake_case | `create_project()` |
| Constants | UPPER_SNAKE_CASE | `MAX_BPM` |
| Private | `_leading_underscore` | `_parse_midi()` |
| Type hints | Built-in + Optional | `Optional[str]`, `list[Project]` |

### Function Documentation

```python
def render_audio(
    song_id: int,
    format: str = 'wav',
    sample_rate: int = 48000,
) -> str:
    """
    Render a song to audio file.

    Args:
        song_id: ID of song to render
        format: Output format ('wav', 'mp3', 'flac')
        sample_rate: Output sample rate in Hz

    Returns:
        Path to rendered audio file

    Raises:
        SongNotFoundError: If song_id doesn't exist
        RenderError: If rendering fails

    Example:
        >>> path = render_audio(42, format='wav')
        >>> print(path)
        '/exports/song_42.wav'
    """
    # implementation
```

### Service Layer Pattern

```python
# services/project_service.py

from typing import Optional
from sqlalchemy.orm import Session
from models import Project as ProjectModel
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

class ProjectService:
    """Handle all project-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_project(self, data: ProjectCreate) -> ProjectResponse:
        """Create a new project."""
        project = ProjectModel(**data.model_dump())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    def get_project(self, project_id: int) -> Optional[ProjectResponse]:
        """Get project by ID."""
        project = self.db.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).first()
        if not project:
            return None
        return ProjectResponse.model_validate(project)

    def list_projects(
        self,
        skip: int = 0,
        limit: int = 50,
        archived: Optional[bool] = None,
    ) -> tuple[list[ProjectResponse], int]:
        """List projects with optional filtering."""
        query = self.db.query(ProjectModel)
        if archived is not None:
            query = query.filter(ProjectModel.archived == archived)
        total = query.count()
        projects = query.offset(skip).limit(limit).all()
        return (
            [ProjectResponse.model_validate(p) for p in projects],
            total,
        )

    def update_project(
        self,
        project_id: int,
        data: ProjectUpdate,
    ) -> Optional[ProjectResponse]:
        """Update project fields."""
        project = self.db.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).first()
        if not project:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    def delete_project(self, project_id: int) -> bool:
        """Delete a project."""
        project = self.db.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).first()
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True
```

### FastAPI Router

```python
# api/projects.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.project_service import ProjectService
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from db import get_db

router = APIRouter(prefix='/projects', tags=['projects'])


@router.get('/', response_model=dict)
def list_projects(
    skip: int = 0,
    limit: int = 50,
    archived: bool | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """List all projects."""
    service = ProjectService(db)
    projects, total = service.list_projects(skip, limit, archived)
    return {
        'projects': projects,
        'total': total,
        'skip': skip,
        'limit': limit,
    }


@router.post('/', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Create a new project."""
    service = ProjectService(db)
    return service.create_project(data)


@router.get('/{project_id}', response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Get project by ID."""
    service = ProjectService(db)
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Project {project_id} not found',
        )
    return project


@router.patch('/{project_id}', response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Update project."""
    service = ProjectService(db)
    project = service.update_project(project_id, data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Project {project_id} not found',
        )
    return project


@router.delete('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete project."""
    service = ProjectService(db)
    if not service.delete_project(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Project {project_id} not found',
        )
```

### Pydantic Schemas

```python
# schemas/project.py

from datetime import datetime
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    project_type: str = Field(default='single', pattern='^(album|ep|single|demo)$')
    description: str | None = None
    genre: str | None = None
    artist_name: str = Field(default='Unknown', max_length=255)
    bpm: int | None = Field(None, ge=30, le=300)
    key: str | None = Field(None, max_length=10)


class ProjectCreate(ProjectBase):
    """Schema for creating projects."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating projects (all fields optional)."""
    name: str | None = None
    description: str | None = None
    genre: str | None = None
    bpm: int | None = None
    key: str | None = None


class ProjectResponse(ProjectBase):
    """Schema for project responses."""
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    archived: bool

    class Config:
        from_attributes = True  # For SQLAlchemy compatibility
```

### Testing

```python
# tests/test_project_service.py

import pytest
from sqlalchemy.orm import Session
from services.project_service import ProjectService
from schemas.project import ProjectCreate


@pytest.fixture
def project_service(db: Session) -> ProjectService:
    """Fixture providing ProjectService with test database."""
    return ProjectService(db)


def test_create_project(project_service: ProjectService) -> None:
    """Test creating a new project."""
    data = ProjectCreate(
        name='Test Project',
        project_type='single',
        genre='Rock',
    )
    project = project_service.create_project(data)
    assert project.id is not None
    assert project.name == 'Test Project'
    assert project.genre == 'Rock'


def test_get_project(project_service: ProjectService) -> None:
    """Test retrieving a project."""
    data = ProjectCreate(name='Test', project_type='single')
    created = project_service.create_project(data)
    retrieved = project_service.get_project(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id


def test_get_nonexistent_project(project_service: ProjectService) -> None:
    """Test retrieving a nonexistent project returns None."""
    result = project_service.get_project(999)
    assert result is None
```

### Error Handling

```python
# utils/exceptions.py

class SonmancerError(Exception):
    """Base exception for Sonmancer."""
    pass


class NotFoundError(SonmancerError):
    """Resource not found."""
    pass


class ValidationError(SonmancerError):
    """Validation failed."""
    pass


class RenderError(SonmancerError):
    """Audio rendering failed."""
    pass
```

---

## Git Workflow

### Commit Messages

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
```
feat(lyrics): Add AI lyric generation for verses

Implement songwriter agent integration with Ollama.
Supports mood, theme, and vocabulary customization.

Closes #42
```

```
fix(audio): Correct sample rate conversion in renderer

Previously used hardcoded 44.1kHz instead of configured sample rate.

Fixes #156
```

### Branch Naming

- Feature: `feature/add-vocal-effects`
- Bug fix: `fix/audio-dropout-issue`
- Documentation: `docs/update-setup-guide`

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Unit tests added
- [ ] Manual testing done
- [ ] No test needed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
```

---

## Documentation

### Inline Comments

```python
# ✅ Good: Explains WHY, not WHAT
# Skip tracks with duration < 1 second to avoid clicks during transitions
if track.duration_seconds < 1.0:
    continue

# ❌ Bad: Explains what code already says
# Increment counter
count += 1
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_loudness(audio_data: np.ndarray, sr: int) -> float:
    """
    Calculate perceived loudness using LUFS standard.

    Args:
        audio_data: Audio samples (mono or stereo)
        sr: Sample rate in Hz

    Returns:
        Loudness in LUFS

    Raises:
        ValueError: If audio_data is empty

    Note:
        Uses ITU-R BS.1770-4 standard weighting.
    """
```

---

## Performance Considerations

### Frontend

- Memoize expensive computations: `useMemo`, `useCallback`
- Lazy load routes: `React.lazy`
- Virtualize long lists: use windowing library
- Debounce search/filter inputs

### Backend

- Use connection pooling for database
- Cache frequently accessed data (genres, models)
- Stream large file uploads/downloads
- Use async endpoints for I/O operations
- Profile before optimizing

