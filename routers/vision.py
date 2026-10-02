"""Vision endpoints: scene description, text reading, image Q&A."""

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Security, status
from services import gemini_service
from dependencies import verify_api_key, validate_image_file

router = APIRouter(
    prefix="/vision",
    tags=["Vision"],
    dependencies=[Security(verify_api_key)],
)
logger = logging.getLogger("sight_companion.vision")


@router.post("/describe-scene")
async def describe_scene(
    image: UploadFile = File(...),
    language: str = Form("en"),
):
    """Describe a scene from a camera image for a visually impaired user."""
    image_bytes, mime_type = await validate_image_file(image)
    try:
        description = await gemini_service.describe_scene(
            image_bytes, language=language, mime_type=mime_type
        )
        return {"description": description}
    except Exception as e:
        logger.error(f"Error in describe_scene: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )


@router.post("/read-text")
async def read_text(
    image: UploadFile = File(...),
):
    """Extract and return readable text from an image (OCR-style)."""
    image_bytes, mime_type = await validate_image_file(image)
    try:
        text = await gemini_service.read_text(
            image_bytes, mime_type=mime_type
        )
        return {"text": text}
    except Exception as e:
        logger.error(f"Error in read_text: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )


@router.post("/ask-about-image")
async def ask_about_image(
    image: UploadFile = File(...),
    question: str = Form(...),
    language: str = Form("en"),
):
    """Ask a question about an image (AI tutor / visual Q&A)."""
    image_bytes, mime_type = await validate_image_file(image)
    try:
        answer = await gemini_service.ask_about_image(
            image_bytes, question=question, language=language, mime_type=mime_type
        )
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error in ask_about_image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )
