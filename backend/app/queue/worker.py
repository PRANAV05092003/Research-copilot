import os
import uuid

import structlog
from arq.connections import RedisSettings
from sqlalchemy import select

from app.ai.ingestion.pdf_parser import PDFParser
from app.api.deps import get_embedding_provider
from app.db.session import AsyncSessionLocal
from app.models import Job, Paper, PaperChunk

logger = structlog.get_logger()

from typing import Any


async def ingest_paper_task(ctx: dict[str, Any], paper_id: uuid.UUID, file_bytes: bytes, user_id: uuid.UUID, workspace_id: uuid.UUID) -> None:
    logger.info(f"Starting ingestion for paper {paper_id}")
    
    # 1. Parse PDF
    parser = PDFParser()
    try:
        pages = parser.parse(file_bytes)
    except Exception as e:
        logger.error(f"Failed to parse PDF {paper_id}", exc_info=e)
        async with AsyncSessionLocal() as db:
            paper = await db.get(Paper, paper_id)
            if paper:
                paper.status = 'failed'
                paper.error_message = str(e)
            
            # Find the job using ref_id=paper_id
            result = await db.execute(select(Job).where(Job.ref_id == paper_id))
            job = result.scalar_one_or_none()
            if job:
                job.status = 'failed'
                job.error = str(e)
            
            await db.commit()
        return

    # 2. Get embeddings
    embedding_provider = await get_embedding_provider()
    
    # 3. Create chunks and save to DB
    async with AsyncSessionLocal() as db:
        # Get Paper and Job
        paper = await db.get(Paper, paper_id)
        if not paper:
            logger.error(f"Paper {paper_id} not found in DB")
            return
            
        result = await db.execute(select(Job).where(Job.ref_id == paper_id))
        job = result.scalar_one_or_none()
        
        if job:
            job.status = 'running'
            await db.commit()
        
        chunks = []
        chunk_index = 0
        
        for page in pages:
            text = page['text']
            if not text:
                continue
                
            # Embed the text
            try:
                vectors = await embedding_provider.embed_documents([text])
                vector = vectors[0]
            except Exception as e:
                logger.error(f"Failed to embed chunk for {paper_id}", exc_info=e)
                continue
            
            chunk = PaperChunk(
                paper_id=paper_id,
                chunk_index=chunk_index,
                text=text,
                page_number=page['page_number'],
                token_count=len(text) // 4,  # Rough estimate
                embedding=vector
            )
            chunks.append(chunk)
            chunk_index += 1
            
        if chunks:
            db.add_all(chunks)
            paper.page_count = len(pages)
            paper.status = 'ready'
            if job:
                job.status = 'succeeded'
                job.progress = 100
        else:
            paper.status = 'failed'
            paper.error_message = 'No extractable text found'
            if job:
                job.status = 'failed'
                job.error = 'No extractable text found'
                
        await db.commit()
        logger.info(f"Finished ingestion for paper {paper_id}, created {len(chunks)} chunks")

async def startup(ctx: dict[str, Any]) -> None:
    pass

async def shutdown(ctx: dict[str, Any]) -> None:
    pass

class WorkerSettings:
    functions = (ingest_paper_task,)
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://redis:6379/0"))
