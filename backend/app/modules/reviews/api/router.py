from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.reviews.api.schemas import (
    ReviewCreateRequest,
    ReviewListResponse,
    ReviewResponse,
)
from app.modules.reviews.application.services import create_review, list_reviews
from app.shared.openapi_helpers import LIST_RESPONSES, MUTATE_RESPONSES

router = APIRouter(prefix="/api/v1/documents", tags=["reviews"])


@router.post(
    "/{document_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a document review",
    description=(
        "Creates a new review for a document with a numeric grade (1–10) "
        "and written feedback.  The reviewing user is recorded automatically."
    ),
    response_description="The newly created review record",
    responses={
        404: {"description": "Document not found"},
        **MUTATE_RESPONSES,
    },
)
def add_review(
    document_id: UUID,
    payload: ReviewCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> ReviewResponse:
    review = create_review(
        session,
        document_id=document_id,
        user_id=current_user.id,
        grade=payload.grade,
        comment=payload.comment,
    )
    return ReviewResponse(
        id=review.id,
        document_id=review.document_id,
        user_id=review.user_id,
        grade=review.grade,
        comment=review.comment,
        created_date=review.created_date,
    )


@router.get(
    "/{document_id}/reviews",
    response_model=ReviewListResponse,
    status_code=status.HTTP_200_OK,
    summary="List reviews for a document",
    description=(
        "Returns a paginated list of all reviews submitted for the specified document, "
        "ordered by creation date (most recent first)."
    ),
    response_description="Paginated list of reviews",
    responses={
        404: {"description": "Document not found"},
        **LIST_RESPONSES,
    },
)
def get_reviews(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page (1–100)"),
) -> ReviewListResponse:
    reviews, total = list_reviews(
        session,
        document_id=document_id,
        page=page,
        page_size=page_size,
    )
    return ReviewListResponse(
        items=[
            ReviewResponse(
                id=review.id,
                document_id=review.document_id,
                user_id=review.user_id,
                grade=review.grade,
                comment=review.comment,
                created_date=review.created_date,
            )
            for review in reviews
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
