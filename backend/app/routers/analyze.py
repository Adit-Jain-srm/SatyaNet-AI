import base64
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import AnalysisRequest, AnalysisResponse, ContentType
from app.services.orchestrator import analyze_content

router = APIRouter(tags=["analysis"])

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    return await analyze_content(request)


@router.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_upload(
    file: UploadFile = File(...),
    content_type: str = Form("image"),
    language: Optional[str] = Form(None),
):
    """Accept multipart file uploads for image, audio, and video analysis."""
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 50 MB limit")

    b64 = base64.b64encode(raw).decode("utf-8")

    ct_map = {
        "image": ContentType.IMAGE,
        "audio": ContentType.AUDIO,
        "video": ContentType.VIDEO,
    }
    if content_type not in ct_map:
        raise HTTPException(status_code=400, detail=f"Invalid content_type: {content_type}. Use image, audio, or video.")
    ct = ct_map[content_type]

    request = AnalysisRequest(
        content=b64,
        content_type=ct,
        language=language,
    )
    return await analyze_content(request)
