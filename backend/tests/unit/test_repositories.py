import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyJobRepository,
    SQLAlchemyPaperRepository,
)
from app.models import Conversation, Job, Paper


@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_paper_repository_get_by_id(mock_session):
    repo = SQLAlchemyPaperRepository(mock_session)
    paper_id = uuid.uuid4()
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Paper(id=paper_id, title="Test Paper")
    mock_session.execute.return_value = mock_result
    
    paper = await repo.get_by_id(paper_id)
    assert paper is not None
    assert paper.title == "Test Paper"
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_paper_repository_create(mock_session):
    repo = SQLAlchemyPaperRepository(mock_session)
    paper = Paper(id=uuid.uuid4(), title="New Paper")
    
    created_paper = await repo.create(paper)
    
    mock_session.add.assert_called_once_with(paper)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(paper)
    assert created_paper.title == "New Paper"

@pytest.mark.asyncio
async def test_conversation_repository_create(mock_session):
    repo = SQLAlchemyConversationRepository(mock_session)
    conv = Conversation(id=uuid.uuid4(), title="New Chat")
    
    created_conv = await repo.create(conv)
    
    mock_session.add.assert_called_once_with(conv)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(conv)
    assert created_conv.title == "New Chat"

@pytest.mark.asyncio
async def test_job_repository_update_status(mock_session):
    repo = SQLAlchemyJobRepository(mock_session)
    job_id = uuid.uuid4()
    job = Job(id=job_id, status="queued")
    
    # Mock get_by_id logic
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = job
    mock_session.execute.return_value = mock_result
    
    updated_job = await repo.update_status(job_id, "completed", 100)
    
    assert updated_job.status == "completed"
    assert updated_job.progress == 100
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(job)
