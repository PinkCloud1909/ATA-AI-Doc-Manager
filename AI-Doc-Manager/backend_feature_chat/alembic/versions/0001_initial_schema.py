"""initial chat schema

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── roles ─────────────────────────────────────────────────────────────────
    op.create_table('roles',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('role_name',   sa.String(50),  nullable=False, unique=True),
        sa.Column('description', sa.Text,        nullable=True),
    )

    # ── privileges ────────────────────────────────────────────────────────────
    op.create_table('privileges',
        sa.Column('id',           postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('role_id',      postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('api_endpoint', sa.String(255), nullable=False),
        sa.Column('is_allowed',   sa.Boolean,     nullable=False, default=True),
    )

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table('users',
        sa.Column('id',                    postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('firebase_uid',          sa.String(128), nullable=False, unique=True),
        sa.Column('username',              sa.String(100), nullable=False),
        sa.Column('email',                 sa.String(255), nullable=False, unique=True),
        sa.Column('last_password_changed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at',            sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_firebase_uid', 'users', ['firebase_uid'])

    # ── user_roles ────────────────────────────────────────────────────────────
    op.create_table('user_roles',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id',     postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role_id',     postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── documents ─────────────────────────────────────────────────────────────
    doc_status = sa.Enum('DRAFT','PENDING_REVIEW','APPROVED','REJECTED','EXPIRED', name='documentstatus')
    doc_type   = sa.Enum('TEMPLATE','CUSTOMER_SPECIFIC','COMMON_GUIDE', name='documenttype')

    op.create_table('documents',
        sa.Column('id',                postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version',           sa.Integer,     nullable=False, default=1),
        sa.Column('document_type',     doc_type,       nullable=False),
        sa.Column('status',            doc_status,     nullable=False),
        sa.Column('gcs_path',          sa.String(1000),nullable=False),
        sa.Column('original_filename', sa.String(500), nullable=False),
        sa.Column('content_type',      sa.String(100), nullable=False),
        sa.Column('size_bytes',        sa.Integer,     nullable=True),
        sa.Column('is_vectorized',     sa.Boolean,     default=False),
        sa.Column('vertex_index_id',   sa.String(500), nullable=True),
        sa.Column('created_by',        postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('modified_by',       postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('modified_date',     sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_documents_group_id', 'documents', ['document_group_id'])

    # ── document_reviews ──────────────────────────────────────────────────────
    op.create_table('document_reviews',
        sa.Column('id',           postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id',  postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('grade',        sa.Integer, nullable=False),
        sa.Column('comment',      sa.Text,    nullable=False),
        sa.Column('user_id',      postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── chat_sessions ─────────────────────────────────────────────────────────
    op.create_table('chat_sessions',
        sa.Column('id',         postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id',    postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title',      sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])

    # ── chat_messages ─────────────────────────────────────────────────────────
    msg_role = sa.Enum('user', 'assistant', name='messagerole')

    op.create_table('chat_messages',
        sa.Column('id',         postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id'), nullable=False),
        sa.Column('role',       msg_role,   nullable=False),
        sa.Column('content',    sa.Text,    nullable=False),
        sa.Column('is_from_kb', sa.Boolean, default=False),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('sources',    postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])


def downgrade() -> None:
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('document_reviews')
    op.drop_table('documents')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('privileges')
    op.drop_table('roles')
    op.execute("DROP TYPE IF EXISTS messagerole")
    op.execute("DROP TYPE IF EXISTS documentstatus")
    op.execute("DROP TYPE IF EXISTS documenttype")
