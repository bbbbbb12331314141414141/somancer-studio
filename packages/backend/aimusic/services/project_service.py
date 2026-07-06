"""Project service business logic."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from aimusic.models.entities import Project as ProjectModel
from aimusic.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService:
    """Handle project operations."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_project(self, data: ProjectCreate) -> ProjectResponse:
        """Create a new project."""
        # Generate slug from name
        slug = data.name.lower().replace(" ", "-").replace("_", "-")

        project = ProjectModel(
            name=data.name,
            slug=slug,
            description=data.description,
            project_type=data.project_type,
            genre=data.genre,
            artist_name=data.artist_name,
            bpm=data.bpm,
            key=data.key,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    def get_project(self, project_id: int) -> Optional[ProjectResponse]:
        """Get project by ID."""
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            return None
        return ProjectResponse.model_validate(project)

    def list_projects(
        self,
        skip: int = 0,
        limit: int = 50,
        archived: Optional[bool] = None,
    ) -> tuple[list[ProjectResponse], int]:
        """List projects with filtering."""
        query = self.db.query(ProjectModel)

        if archived is not None:
            query = query.filter(ProjectModel.archived == archived)

        total = query.count()
        projects = query.order_by(desc(ProjectModel.created_at)).offset(skip).limit(limit).all()

        return (
            [ProjectResponse.model_validate(p) for p in projects],
            total,
        )

    def update_project(
        self,
        project_id: int,
        data: ProjectUpdate,
    ) -> Optional[ProjectResponse]:
        """Update project."""
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)

        self.db.commit()
        self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    def delete_project(self, project_id: int) -> bool:
        """Delete project."""
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            return False

        self.db.delete(project)
        self.db.commit()
        return True
