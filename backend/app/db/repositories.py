import abc
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Job, Message, Paper


class PaperRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, paper_id: uuid.UUID) -> Paper | None:
        pass

    @abc.abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID, limit: int = 20) -> list[Paper]:
        pass

    @abc.abstractmethod
    async def create(self, paper: Paper) -> Paper:
        pass


class ConversationRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, conv_id: uuid.UUID) -> Conversation | None:
        pass

    @abc.abstractmethod
    async def create(self, conversation: Conversation) -> Conversation:
        pass

    @abc.abstractmethod
    async def list_by_workspace(
        self, workspace_id: uuid.UUID, limit: int = 20
    ) -> list[Conversation]:
        pass

    @abc.abstractmethod
    async def get_messages(self, conv_id: uuid.UUID) -> list[Message]:
        pass

    @abc.abstractmethod
    async def add_message(self, message: Message) -> Message:
        pass


class JobRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
        pass

    @abc.abstractmethod
    async def create(self, job: Job) -> Job:
        pass

    @abc.abstractmethod
    async def update_status(
        self, job_id: uuid.UUID, status: str, progress: int = 0, error: str | None = None
    ) -> Job | None:
        pass


class SQLAlchemyPaperRepository(PaperRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, paper_id: uuid.UUID) -> Paper | None:
        stmt = select(Paper).where(Paper.id == paper_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: uuid.UUID, limit: int = 20) -> list[Paper]:
        stmt = (
            select(Paper)
            .where(Paper.workspace_id == workspace_id)
            .order_by(Paper.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, paper: Paper) -> Paper:
        self.session.add(paper)
        await self.session.commit()
        await self.session.refresh(paper)
        return paper


class SQLAlchemyConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, conv_id: uuid.UUID) -> Conversation | None:
        stmt = select(Conversation).where(Conversation.id == conv_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def list_by_workspace(
        self, workspace_id: uuid.UUID, limit: int = 20
    ) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.workspace_id == workspace_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_messages(self, conv_id: uuid.UUID) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_message(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message


class SQLAlchemyJobRepository(JobRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
        stmt = select(Job).where(Job.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, job: Job) -> Job:
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update_status(
        self, job_id: uuid.UUID, status: str, progress: int = 0, error: str | None = None
    ) -> Job | None:
        job = await self.get_by_id(job_id)
        if job:
            job.status = status
            job.progress = progress
            if error:
                job.error = error
            await self.session.commit()
            await self.session.refresh(job)
        return job
