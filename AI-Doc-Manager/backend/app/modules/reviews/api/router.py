from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.core.exceptions import ForbiddenError
from app.modules.documents.application.services import get_document_by_id
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.reviews.api.schemas import ReviewCreateRequest, ReviewResponse
from app.modules.reviews.application.services import create_review, list_reviews, list_all_reviews
from app.shared.enums import Status

router = APIRouter(prefix="/api/v1/documents", tags=["reviews"])
reviews_router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])

ROLE_VISIBLE_STATUSES: dict[str, set[Status]] = {
    "user": {Status.APPROVED, Status.EXPIRED},
    "viewer": {Status.APPROVED, Status.EXPIRED},
    "editor": {
        Status.DRAFT,
        Status.PENDING_REVIEW,
        Status.APPROVED,
        Status.REJECTED,
        Status.EXPIRED,
    },
    "reviewer": {
        Status.PENDING_REVIEW,
        Status.APPROVED,
        Status.REJECTED,
        Status.EXPIRED,
    },
}


def _ensure_can_view_document(
    current_user: AuthenticatedUser,
    session: Session,
    document_id: UUID,
) -> None:
    role_names = {role_name.lower() for role_name in current_user.roles}
    if "admin" in role_names:
        return

    allowed_statuses: set[Status] = set()
    for role_name in role_names:
        allowed_statuses.update(ROLE_VISIBLE_STATUSES.get(role_name, set()))

    document = get_document_by_id(session, document_id)
    if document.status not in allowed_statuses:
        raise ForbiddenError("You do not have access to this document")


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
    _ensure_can_view_document(current_user, session, document_id)
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
    _ensure_can_view_document(current_user, session, document_id)
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


@reviews_router.get(
    "",
    response_model=list[ReviewResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_reviews(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[ReviewResponse]:
    reviews = list_all_reviews(session)
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
