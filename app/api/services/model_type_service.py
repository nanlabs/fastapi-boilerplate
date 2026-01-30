"""Model type service for business logic."""

from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, SortingValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.model_type import ModelTypeResponse
from app.api.services.utils import apply_sorting, build_list_response
from app.db.models.model_type import ModelType
from app.schemas.common.base import ModelTypeStatus


class ModelTypeService:
    """Service for model type business logic."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session."""
        self.db = db

    def get_model_type(self, model_type_id: int) -> ModelTypeResponse:
        """Get a model type by ID."""
        model_type = (
            self.db.query(ModelType)
            .filter(ModelType.id == model_type_id)
            .filter(ModelType.deleted_at.is_(None))
            .first()
        )
        if not model_type:
            raise NotFoundError(f"Model type with ID {model_type_id} not found")

        return self._build_model_type_response(model_type)

    def list_model_types(
        self,
        pagination: PaginationParams,
        sorting: SortingParams,
        search_params: SearchParams,
    ) -> ListResponse[ModelTypeResponse]:
        """List all model types with pagination, sorting, and search."""
        query = self.db.query(ModelType).filter(ModelType.deleted_at.is_(None))

        # Apply search filter
        if search_params.search:
            query = query.filter(ModelType.name.ilike(f"%{search_params.search}%"))

        # Apply sorting
        if sorting.sort_by:
            if sorting.sort_by not in ModelType.valid_sort_fields:
                raise SortingValidationError(
                    f"Invalid sort field '{sorting.sort_by}'. "
                    f"Valid fields are: {', '.join(sorted(ModelType.valid_sort_fields))}"
                )
            sort_column = getattr(ModelType, sorting.sort_by)
            query = apply_sorting(query, sort_column, sorting.sort_direction)
        else:
            # Default sort by id ascending
            query = query.order_by(ModelType.id.asc())

        model_types = query.offset(pagination.skip).limit(pagination.limit).all()

        data = [self._build_model_type_response(model_type) for model_type in model_types]

        return build_list_response(pagination, sorting, search_params, data)

    def _build_model_type_response(self, model_type: ModelType) -> ModelTypeResponse:
        """Build a ModelTypeResponse from a ModelType model."""
        return ModelTypeResponse(
            id=model_type.id,
            name=model_type.name,
            description=model_type.description,
            enabled=model_type.enabled,
            status=ModelTypeStatus(model_type.status),
        )
