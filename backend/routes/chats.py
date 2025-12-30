"""
Chat history CRUD routes.
Handles chat sessions, messages, and image attachments.
"""

import os
import hashlib
import shutil
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.engine import get_db
from db.models import User, Chat, Message, Attachment
from routes.auth import get_current_user

router = APIRouter(prefix="/api/chats", tags=["chats"])

# Upload directory
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


# ============================================================================
# Schemas
# ============================================================================

class ChatCreate(BaseModel):
    title: str = Field(default="New Chat", max_length=200)


class ChatUpdate(BaseModel):
    title: str = Field(..., max_length=200)


class ChatResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message_preview: Optional[str] = None

    class Config:
        from_attributes = True


class AttachmentResponse(BaseModel):
    id: int
    type: str
    file_path: str
    original_filename: Optional[str]
    mime_type: Optional[str]

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    attachments: List[AttachmentResponse] = []
    egl_result_json: Optional[str] = None
    food_analysis_json: Optional[str] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    egl_result_json: Optional[str] = None
    food_analysis_json: Optional[str] = None


class ChatWithMessages(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


# ============================================================================
# Helper functions
# ============================================================================

def ensure_upload_dir(user_id: int, chat_id: int) -> str:
    """Ensure upload directory exists and return path"""
    upload_path = os.path.join(UPLOADS_DIR, str(user_id), str(chat_id))
    os.makedirs(upload_path, exist_ok=True)
    return upload_path


def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


# ============================================================================
# Chat CRUD Routes
# ============================================================================

@router.get("", response_model=List[ChatResponse])
async def list_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """List all chats for the current user"""
    query = select(Chat).where(Chat.user_id == current_user.id)
    
    if search:
        query = query.where(Chat.title.ilike(f"%{search}%"))
    
    query = query.order_by(desc(Chat.updated_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    chats = result.scalars().all()
    
    # Get message counts and previews
    chat_responses = []
    for chat in chats:
        msg_result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()
        
        count_result = await db.execute(
            select(Message).where(Message.chat_id == chat.id)
        )
        msg_count = len(count_result.scalars().all())
        
        chat_responses.append(ChatResponse(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            message_count=msg_count,
            last_message_preview=last_msg.content[:100] if last_msg else None,
        ))
    
    return chat_responses


@router.post("", response_model=ChatResponse)
async def create_chat(
    request: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new chat"""
    chat = Chat(
        user_id=current_user.id,
        title=request.title,
    )
    db.add(chat)
    await db.flush()
    
    return ChatResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        message_count=0,
    )


@router.get("/{chat_id}", response_model=ChatWithMessages)
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a chat with all its messages"""
    result = await db.execute(
        select(Chat)
        .options(selectinload(Chat.messages).selectinload(Message.attachments))
        .where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return ChatWithMessages(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                attachments=[
                    AttachmentResponse(
                        id=att.id,
                        type=att.type,
                        file_path=att.file_path,
                        original_filename=att.original_filename,
                        mime_type=att.mime_type,
                    ) for att in msg.attachments
                ],
                egl_result_json=msg.egl_result_json,
                food_analysis_json=msg.food_analysis_json,
            ) for msg in chat.messages
        ],
    )


@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    request: ChatUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update chat title"""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat.title = request.title
    chat.updated_at = datetime.utcnow()
    
    return ChatResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
    )


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a chat and all its messages"""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Delete upload directory for this chat
    upload_path = os.path.join(UPLOADS_DIR, str(current_user.id), str(chat_id))
    if os.path.exists(upload_path):
        shutil.rmtree(upload_path)
    
    await db.delete(chat)
    
    return {"message": "Chat deleted successfully"}


# ============================================================================
# Message Routes
# ============================================================================

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
):
    """Get messages for a chat"""
    # Verify chat ownership
    chat_result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    if not chat_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chat not found")
    
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.attachments))
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at)
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            attachments=[
                AttachmentResponse(
                    id=att.id,
                    type=att.type,
                    file_path=att.file_path,
                    original_filename=att.original_filename,
                    mime_type=att.mime_type,
                ) for att in msg.attachments
            ],
            egl_result_json=msg.egl_result_json,
            food_analysis_json=msg.food_analysis_json,
        ) for msg in messages
    ]


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def create_message(
    chat_id: int,
    request: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a message to a chat"""
    # Verify chat ownership
    chat_result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    message = Message(
        chat_id=chat_id,
        role=request.role,
        content=request.content,
        egl_result_json=request.egl_result_json,
        food_analysis_json=request.food_analysis_json,
    )
    db.add(message)
    
    # Update chat timestamp
    chat.updated_at = datetime.utcnow()
    
    # Auto-generate chat title from first user message
    if request.role == "user" and chat.title == "New Chat":
        chat.title = request.content[:50] + ("..." if len(request.content) > 50 else "")
    
    await db.flush()
    
    return MessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
        attachments=[],
        egl_result_json=message.egl_result_json,
        food_analysis_json=message.food_analysis_json,
    )


# ============================================================================
# Image Upload Routes
# ============================================================================

@router.post("/{chat_id}/image", response_model=MessageResponse)
async def upload_image(
    chat_id: int,
    file: UploadFile = File(...),
    message_content: str = Form(default="Analyze this food"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload an image and create a user message with attachment"""
    # Verify chat ownership
    chat_result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create upload directory
    upload_path = ensure_upload_dir(current_user.id, chat_id)
    
    # Generate unique filename
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    unique_filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(upload_path, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Compute hash
    file_hash = compute_file_hash(file_path)
    
    # Create message
    message = Message(
        chat_id=chat_id,
        role="user",
        content=message_content,
    )
    db.add(message)
    await db.flush()
    
    # Create attachment
    relative_path = f"{current_user.id}/{chat_id}/{unique_filename}"
    attachment = Attachment(
        message_id=message.id,
        type="image",
        file_path=relative_path,
        original_filename=file.filename,
        mime_type=file.content_type,
        file_size=len(content),
        sha256=file_hash,
    )
    db.add(attachment)
    
    # Update chat timestamp and title
    chat.updated_at = datetime.utcnow()
    if chat.title == "New Chat":
        chat.title = f"Food analysis - {datetime.utcnow().strftime('%b %d')}"
    
    await db.flush()
    
    return MessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
        attachments=[
            AttachmentResponse(
                id=attachment.id,
                type=attachment.type,
                file_path=attachment.file_path,
                original_filename=attachment.original_filename,
                mime_type=attachment.mime_type,
            )
        ],
    )


@router.get("/uploads/{user_id}/{chat_id}/{filename}")
async def serve_upload(
    user_id: int,
    chat_id: int,
    filename: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Serve an uploaded file (only to the owner)"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = os.path.join(UPLOADS_DIR, str(user_id), str(chat_id), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

