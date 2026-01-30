"""Experiment type service for business logic."""

from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, SortingValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.experiment_type import ExperimentTypeResponse
from app.api.services.utils import apply_sorting, build_list_response
from app.db.models.experiment_type import ExperimentType


class ExperimentTypeService:
    """Service for experiment type business logic."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session."""
        self.db = db

    def get_experiment_type(self, experiment_type_id: int) -> ExperimentTypeResponse:
        """Get an experiment type by ID."""
        experiment_type = (
            self.db.query(ExperimentType)
            .filter(ExperimentType.id == experiment_type_id)
            .filter(ExperimentType.deleted_at.is_(None))
            .first()
        )
        if not experiment_type:
            raise NotFoundError(f"Experiment type with ID {experiment_type_id} not found")

        return self._build_experiment_type_response(experiment_type)

    def list_experiment_types(
        self,
        pagination: PaginationParams,
        sorting: SortingParams,
        search_params: SearchParams,
    ) -> ListResponse[ExperimentTypeResponse]:
        """List all experiment types with pagination, sorting, and search."""
        query = self.db.query(ExperimentType).filter(ExperimentType.deleted_at.is_(None))

        # Apply search filter
        if search_params.search:
            query = query.filter(ExperimentType.name.ilike(f"%{search_params.search}%"))

        # Apply sorting
        if sorting.sort_by:
            if sorting.sort_by not in ExperimentType.valid_sort_fields:
                raise SortingValidationError(
                    f"Invalid sort field '{sorting.sort_by}'. "
                    f"Valid fields are: {', '.join(sorted(ExperimentType.valid_sort_fields))}"
                )
            sort_column = getattr(ExperimentType, sorting.sort_by)
            query = apply_sorting(query, sort_column, sorting.sort_direction)
        else:
            # Default sort by id ascending
            query = query.order_by(ExperimentType.id.asc())

        experiment_types = query.offset(pagination.skip).limit(pagination.limit).all()

        data = [self._build_experiment_type_response(exp_type) for exp_type in experiment_types]

        return build_list_response(pagination, sorting, search_params, data)

    def _build_experiment_type_response(
        self, experiment_type: ExperimentType
    ) -> ExperimentTypeResponse:
        """Build an ExperimentTypeResponse from an ExperimentType model."""
        return ExperimentTypeResponse(
            id=experiment_type.id,
            name=experiment_type.name,
        )
