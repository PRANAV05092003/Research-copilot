import typing
import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_conv_repo, get_conversation_service, get_current_user
from app.core.errors import AppError
from app.db.repositories import SQLAlchemyConversationRepository
from app.models import User
from app.schemas.chat import ConversationDetailOut, ConversationOut, MessageCreate, MessageOut
from app.schemas.common import Page
from app.services.interfaces import ConcreteConversationService

router = APIRouter()

@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(
    service: ConcreteConversationService = Depends(get_conversation_service),
    current_user: User = Depends(get_current_user)
) -> typing.Any:
    workspace_id = uuid.uuid5(uuid.NAMESPACE_DNS, "default_workspace")
    
    # We expect a body with 'title' and 'mode' in reality, but this route currently has no body param.
    # We will use defaults for the scaffolded route.
    conv = await service.create_conversation("New Chat", current_user.id, workspace_id, "chat")
    return conv

@router.get("", response_model=Page[ConversationOut])
async def list_conversations(
    cursor: str | None = None, limit: int = 20,
    repo: SQLAlchemyConversationRepository = Depends(get_conv_repo),
    current_user: User = Depends(get_current_user)
) -> typing.Any:
    workspace_id = uuid.uuid5(uuid.NAMESPACE_DNS, "default_workspace")
    convs = await repo.list_by_workspace(workspace_id, limit)
    return Page(items=convs, next_cursor=None, count=len(convs))

@router.get("/{id}", response_model=ConversationDetailOut)
async def get_conversation(
    id: uuid.UUID,
    repo: SQLAlchemyConversationRepository = Depends(get_conv_repo),
    current_user: User = Depends(get_current_user)
) -> typing.Any:
    conv = await repo.get_by_id(id)
    if not conv:
        raise AppError(status_code=404, title="Not Found", detail="Conversation not found")
        
    messages = await repo.get_messages(id)
    conv.messages = messages
    return conv

@router.post("/{id}/messages", response_model=MessageOut)
async def send_message(
    id: uuid.UUID,
    message: MessageCreate,
    repo: SQLAlchemyConversationRepository = Depends(get_conv_repo),
    service: ConcreteConversationService = Depends(get_conversation_service),
    current_user: User = Depends(get_current_user)
) -> typing.Any:
    conv = await repo.get_by_id(id)
    if not conv:
        raise AppError(status_code=404, title="Not Found", detail="Conversation not found")
        
    assistant_msg = await service.send_message(id, message.content)
    return assistant_msg
