"""Tests for the standard APIResponse envelope."""

from datetime import UTC, datetime

from app.api.schemas.common.params import PaginationParams, SearchParams, SortingParams
from app.api.schemas.common.responses import (
    APIResponse,
    ErrorDetail,
    PaginationMeta,
    ResponseMetadata,
    make_error_response,
    make_item_response,
    make_list_response,
)


def _meta(request_id: str = "test-id") -> ResponseMetadata:
    return ResponseMetadata(request_id=request_id, timestamp=datetime.now(UTC))


class TestAPIResponse:
    def test_success_response_structure(self) -> None:
        resp = APIResponse[str](
            success=True,
            status_code=200,
            dev_code="OK",
            message="Done",
            data="hello",
            errors=[],
            metadata=_meta(),
        )
        assert resp.success is True
        assert resp.data == "hello"
        assert resp.errors == []

    def test_error_response_has_null_data(self) -> None:
        resp = APIResponse[None](
            success=False,
            status_code=404,
            dev_code="NOT_FOUND",
            message="Not found",
            data=None,
            errors=[ErrorDetail(message="Resource not found")],
            metadata=_meta(),
        )
        assert resp.success is False
        assert resp.data is None
        assert len(resp.errors) == 1

    def test_error_detail_field_optional(self) -> None:
        err = ErrorDetail(message="Required field missing")
        assert err.field is None

        err_with_field = ErrorDetail(field="name", message="Too short")
        assert err_with_field.field == "name"


class TestResponseMetadata:
    def test_metadata_with_pagination(self) -> None:
        meta = ResponseMetadata(
            request_id="abc",
            timestamp=datetime.now(UTC),
            pagination=PaginationMeta(skip=0, limit=10, total=42),
            sort=SortingParams(),
            search=SearchParams(),
        )
        assert meta.pagination is not None
        assert meta.pagination.total == 42

    def test_metadata_without_pagination(self) -> None:
        meta = _meta()
        assert meta.pagination is None
        assert meta.sort is None


class TestHelpers:
    def test_make_item_response(self) -> None:
        resp = make_item_response(
            data={"id": 1},
            dev_code="PROJECT_RETRIEVED",
            message="Project retrieved",
            request_id="req-1",
        )
        assert resp.success is True
        assert resp.status_code == 200
        assert resp.data == {"id": 1}

    def test_make_list_response(self) -> None:
        resp = make_list_response(
            data=[{"id": 1}],
            total=1,
            pagination=PaginationParams(),
            sorting=SortingParams(),
            search=SearchParams(),
            dev_code="PROJECTS_LISTED",
            message="Projects retrieved",
            request_id="req-1",
        )
        assert resp.success is True
        assert len(resp.data) == 1  # type: ignore[arg-type]
        assert resp.metadata.pagination is not None
        assert resp.metadata.pagination.total == 1

    def test_make_error_response(self) -> None:
        resp = make_error_response(
            status_code=404,
            dev_code="PROJECT_NOT_FOUND",
            message="Project not found",
            request_id="req-1",
        )
        assert resp.success is False
        assert resp.status_code == 404
        assert resp.data is None
