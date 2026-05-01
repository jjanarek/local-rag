from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from api.dependencies import get_ingestion_pipeline
from core.models import IngestionResult

if TYPE_CHECKING:
    from core.processor import IngestionPipeline

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/file", response_model=IngestionResult)
async def ingest_file(
    file: UploadFile,
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline),  # noqa: B008
) -> IngestionResult:
    """
    Upload and process a document into the vector database.
    """
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in [".pdf", ".txt", ".md"]:
        raise HTTPException(
            status_code=400, detail=f"File extension {suffix} not supported. Use PDF, TXT, or MD."
        )

    # Save the incoming file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        try:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
        finally:
            file.file.close()

    # Process the file
    try:
        result = await pipeline.ingest_file(tmp_path, original_filename=file.filename)
        if result.status == "error":
            raise HTTPException(status_code=500, detail=result.message)
        return result
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
