"""rename project to name

Revision ID: 0f449872a150
Revises: 7f322a63d4fe
Create Date: 2025-06-03 23:09:50.753395

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '0f449872a150'
down_revision = '7f322a63d4fe'
branch_labels = None
depends_on = None


def upgrade():
    # Verificare se esistono tabelle temporanee e rimuoverle
    conn = op.get_bind()
    conn.execute(text("DROP TABLE IF EXISTS _alembic_tmp_milestone"))
    conn.execute(text("DROP TABLE IF EXISTS _alembic_tmp_project"))

    # Per la tabella milestone
    # Verifica se la colonna name esiste già
    inspector = sa.inspect(conn)
    milestone_columns = [col['name'] for col in inspector.get_columns('milestone')]

    if 'name' not in milestone_columns:
        with op.batch_alter_table('milestone', schema=None) as batch_op:
            batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=True))

        # Copia i dati da title a name
        op.execute('UPDATE milestone SET name = title')

        # Rendi name NOT NULL e rimuovi title
        with op.batch_alter_table('milestone', schema=None) as batch_op:
            batch_op.alter_column('name', nullable=False)
            batch_op.drop_column('title')

    # Per la tabella project
    project_columns = [col['name'] for col in inspector.get_columns('project')]

    if 'name' not in project_columns:
        with op.batch_alter_table('project', schema=None) as batch_op:
            batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=True))

        # Copia i dati da title a name
        op.execute('UPDATE project SET name = title')

        # Rendi name NOT NULL e rimuovi title
        with op.batch_alter_table('project', schema=None) as batch_op:
            batch_op.alter_column('name', nullable=False)
            batch_op.drop_column('title')

    # Le modifiche alla tabella task
    task_columns = [col['name'] for col in inspector.get_columns('task')]

    if 'completed' not in task_columns:
        with op.batch_alter_table('task', schema=None) as batch_op:
            batch_op.add_column(sa.Column('completed', sa.Boolean(), nullable=True))

    if 'created_at' not in task_columns:
        with op.batch_alter_table('task', schema=None) as batch_op:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    if 'description' not in task_columns:
        with op.batch_alter_table('task', schema=None) as batch_op:
            batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # Verificare se esistono tabelle temporanee e rimuoverle
    conn = op.get_bind()
    conn.execute(text("DROP TABLE IF EXISTS _alembic_tmp_milestone"))
    conn.execute(text("DROP TABLE IF EXISTS _alembic_tmp_project"))

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('description')
        batch_op.drop_column('created_at')
        batch_op.drop_column('completed')

    # Per project
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.VARCHAR(length=100), nullable=True))

    # Copia i dati da name a title
    op.execute('UPDATE project SET title = name')

    # Rendi title NOT NULL e rimuovi name
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.alter_column('title', nullable=False)
        batch_op.drop_column('name')

    # Per milestone
    with op.batch_alter_table('milestone', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.VARCHAR(length=100), nullable=True))

    # Copia i dati da name a title
    op.execute('UPDATE milestone SET title = name')

    # Rendi title NOT NULL e rimuovi name
    with op.batch_alter_table('milestone', schema=None) as batch_op:
        batch_op.alter_column('title', nullable=False)
        batch_op.drop_column('name')
