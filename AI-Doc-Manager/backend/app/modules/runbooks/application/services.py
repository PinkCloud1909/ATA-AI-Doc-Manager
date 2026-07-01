import logging
import uuid
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.documents.domain.models import Document
from app.modules.runbooks.application.runbook_service import RunbookService
from app.modules.runbooks.domain.agent import active_document_ids, active_purpose
from app.modules.runbooks.domain.models import Runbook
from app.shared.utils import utcnow

logger = logging.getLogger(__name__)

runbook_service = RunbookService()


async def generate_runbook_task(
    session: Session,
    *,
    document_ids: list[UUID],
    purpose: str,
    title: str | None,
    user_id: UUID,
) -> Runbook:
    # 1. Validate documents exist
    docs = (
        session.execute(select(Document).where(Document.id.in_(document_ids)))
        .scalars()
        .all()
    )

    found_ids = {doc.id for doc in docs}
    missing_ids = [str(did) for did in document_ids if did not in found_ids]
    if missing_ids:
        raise NotFoundError(f"Documents not found: {', '.join(missing_ids)}")

    # Validate documents are vectorized
    non_vectorized = [doc.title for doc in docs if not doc.is_vectorized]
    if non_vectorized:
        raise ValidationError(
            f"The following documents are not vectorized yet: {', '.join(non_vectorized)}. "
            "Please approve and wait for vectorization before generating a runbook."
        )

    # Resolve title
    resolved_title = (
        title
        or f"Runbook for {purpose.replace('_', ' ').title()} - {utcnow().strftime('%Y-%m-%d %H:%M')}"
    )

    # 2. Create the runbook record in database
    now = utcnow()
    runbook = Runbook(
        title=resolved_title,
        purpose=purpose,
        document_ids=[str(did) for did in document_ids],
        status="generating",
        created_by=user_id,
        created_at=now,
        modified_date=now,
    )
    session.add(runbook)
    session.commit()

    # 3. Call the ADK service to generate the runbook
    # We use contextvars to pass document_ids and purpose to the agent's tool
    token_ids = active_document_ids.set([str(did) for did in document_ids])
    token_purpose = active_purpose.set(purpose)

    session_id = str(uuid.uuid4())
    prompt = f"Please generate a technical runbook for the purpose '{purpose}' with the title '{resolved_title}' using the selected documents."

    try:
        content = await runbook_service.generate(
            user_id=str(user_id),
            session_id=session_id,
            prompt=prompt,
        )
        # Update runbook status
        runbook.content = content
        runbook.status = "completed"
        logger.info(
            "runbook_generation_success",
            extra={"runbook_id": str(runbook.id), "title": resolved_title},
        )
    except Exception as exc:
        logger.error(
            "runbook_generation_failed",
            extra={"runbook_id": str(runbook.id), "error": str(exc)},
        )
        runbook.status = "failed"
        runbook.error_message = str(exc)
    finally:
        active_document_ids.reset(token_ids)
        active_purpose.reset(token_purpose)

    runbook.modified_date = utcnow()
    session.commit()
    return runbook


def get_runbook_by_id(session: Session, runbook_id: UUID) -> Runbook:
    runbook = session.execute(
        select(Runbook).where(Runbook.id == runbook_id)
    ).scalar_one_or_none()
    if runbook is None:
        raise NotFoundError("Runbook not found")
    return runbook


def list_runbooks(
    session: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    created_by: UUID | None = None,
) -> tuple[list[Runbook], int]:
    query = select(Runbook)
    count_query = select(func.count()).select_from(Runbook)

    if created_by is not None:
        query = query.where(Runbook.created_by == created_by)
        count_query = count_query.where(Runbook.created_by == created_by)

    total = session.execute(count_query).scalar() or 0
    offset = (page - 1) * page_size
    query = query.order_by(Runbook.created_at.desc()).offset(offset).limit(page_size)
    runbooks = session.execute(query).scalars().all()

    return runbooks, total


def delete_runbook(session: Session, runbook_id: UUID) -> None:
    runbook = get_runbook_by_id(session, runbook_id)
    session.delete(runbook)
    session.commit()
    logger.info("runbook_deleted", extra={"runbook_id": str(runbook_id)})
