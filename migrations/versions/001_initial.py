"""Initial migration with all models

Revision ID: 001
Revises: 
Create Date: 2025-02-07 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create all tables
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=False),
        sa.Column('user_type', sa.String(length=10), nullable=False),
        sa.Column('role', sa.String(length=10), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('is_claimed', sa.Boolean(), nullable=False),
        sa.Column('profile_consent', sa.Boolean(), nullable=False),
        sa.Column('verification_token', sa.String(length=100), nullable=True),
        sa.Column('verification_token_created_at', sa.DateTime(), nullable=True),
        sa.Column('reset_token', sa.String(length=100), nullable=True),
        sa.Column('reset_token_created_at', sa.DateTime(), nullable=True),
        sa.Column('password_is_temporary', sa.Boolean(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('last_online', sa.DateTime(), nullable=True),
        sa.Column('dark_mode', sa.Boolean(), nullable=False),
        sa.Column('search_history', sa.Text(), nullable=True),
        sa.Column('total_upvotes', sa.Integer(), nullable=False),
        sa.Column('reliable_tag', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    op.create_table('lecturer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('claimed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['claimed_by_user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    op.create_table('subject',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject_code', sa.String(length=100), nullable=True),
        sa.Column('subject_name', sa.String(length=100), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('review',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('review_text', sa.Text(), nullable=False),
        sa.Column('rating_clarity', sa.Integer(), nullable=False),
        sa.Column('rating_engagement', sa.Integer(), nullable=False),
        sa.Column('rating_punctuality', sa.Integer(), nullable=False),
        sa.Column('rating_responsiveness', sa.Integer(), nullable=False),
        sa.Column('rating_fairness', sa.Integer(), nullable=False),
        sa.Column('recommend', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lecturer_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=True),
        sa.Column('review_date', sa.DateTime(), nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False),
        sa.Column('is_pinned', sa.Boolean(), nullable=False),
        sa.Column('subject_code', sa.String(length=100), nullable=True),
        sa.Column('upvotes', sa.Integer(), nullable=False),
        sa.Column('downvotes', sa.Integer(), nullable=False),
        sa.Column('moderation_flags', sa.Text(), nullable=True),
        sa.Column('moderation_severity', sa.String(length=20), nullable=True),
        sa.Column('requires_human_review', sa.Boolean(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('moderated_by_id', sa.Integer(), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.Column('moderation_action', sa.String(length=20), nullable=True),
        sa.Column('ascii_art_score', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['lecturer_id'], ['lecturer.id'], ),
        sa.ForeignKeyConstraint(['moderated_by_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('reply',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reply_text', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('reply_date', sa.DateTime(), nullable=False),
        sa.Column('is_edited', sa.Boolean(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('upvotes', sa.Integer(), nullable=False),
        sa.Column('downvotes', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['review.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('report',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=True),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('report_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reporter_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['review_id'], ['review.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('suggestion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False),
        sa.Column('upvotes', sa.Integer(), nullable=False),
        sa.Column('downvotes', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('ascii_art_score', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('suggestion_vote',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('suggestion_id', sa.Integer(), nullable=False),
        sa.Column('vote_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['suggestion_id'], ['suggestion.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('review_vote',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('vote_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['review.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('reply_vote',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reply_id', sa.Integer(), nullable=False),
        sa.Column('vote_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reply_id'], ['reply.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('role', sa.String(length=10), nullable=True),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('bug_report',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('reported_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('ascii_art_score', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('bug_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bug_report_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bug_report_id'], ['bug_report.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('changelog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version')
    )


def downgrade():
    op.drop_table('changelog')
    op.drop_table('bug_comment')
    op.drop_table('bug_report')
    op.drop_table('audit_log')
    op.drop_table('reply_vote')
    op.drop_table('review_vote')
    op.drop_table('suggestion_vote')
    op.drop_table('suggestion')
    op.drop_table('report')
    op.drop_table('reply')
    op.drop_table('review')
    op.drop_table('subject')
    op.drop_table('lecturer')
    op.drop_table('user')
