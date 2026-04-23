from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.reviews.api.schemas import ReviewCreateRequest, ReviewResponse
from app.modules.reviews.application.services import create_review, list_reviews

router = APIRouter(prefix="/api/v1/documents", tags=["reviews"])


@router.post(
    "/{document_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
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
    response_model=list[ReviewResponse],
    status_code=status.HTTP_200_OK,
)
def get_reviews(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[ReviewResponse]:
    reviews = list_reviews(session, document_id=document_id)
    return [
        ReviewResponse(
            id=review.id,
            document_id=review.document_id,
            user_id=review.user_id,
            grade=review.grade,
            comment=review.comment,
            created_date=review.created_date,
        )
        for review in reviews
    ]
